import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from kenya_kuccps.models import (
    Institution, InstitutionType,
    Programme, ProgrammeOffering, DegreeCutoff,
)


def to_decimal(value):
    """Convert a JSON number or null to Decimal."""
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


class Command(BaseCommand):
    help = "Import degree programme cut-off data from a JSON file."

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            help="Path to the degree_cutoffs.json file.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing DegreeCutoff records before importing.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        json_path = Path(options["json_file"])
        if not json_path.exists():
            self.stderr.write(self.style.ERROR(f"File not found: {json_path}"))
            return

        with open(json_path, "r") as f:
            data = json.load(f)

        programmes_data = data.get("programmes", [])
        if not programmes_data:
            self.stderr.write(self.style.ERROR("No programmes found in JSON."))
            return

        if options["clear"]:
            deleted = DegreeCutoff.objects.all().delete()[0]
            self.stdout.write(f"Cleared {deleted} degree cutoff records.")

        # Build lookup: programme_code -> ProgrammeOffering
        offering_lookup = {}
        for o in ProgrammeOffering.objects.select_related("institution"):
            offering_lookup[o.programme_code] = o

        # Build institution lookup for creating missing offerings
        inst_lookup = {inst.name.upper(): inst for inst in Institution.objects.all()}

        created_offerings = 0
        created_cutoffs = 0
        skipped = []

        for entry in programmes_data:
            code = entry["programme_code"]
            offering = offering_lookup.get(code)

            if not offering:
                # Try to find the institution and create a ProgrammeOffering
                inst_name = entry["institution"].upper()
                institution = inst_lookup.get(inst_name)

                if not institution:
                    # Try prefix match (institution names may differ slightly)
                    for db_name, inst in inst_lookup.items():
                        if inst_name.startswith(db_name) or db_name.startswith(inst_name):
                            institution = inst
                            break

                if not institution:
                    # Create the institution
                    inst_type, _ = InstitutionType.objects.get_or_create(name="Public")
                    max_num = Institution.objects.order_by("-kuccps_number").values_list(
                        "kuccps_number", flat=True
                    ).first() or 0
                    institution = Institution.objects.create(
                        kuccps_number=max_num + 1,
                        code=entry["institution"].title()[:50],
                        name=entry["institution"].title(),
                        institution_type=inst_type,
                    )
                    inst_lookup[institution.name.upper()] = institution

                # Find a parent Programme to link to (use category as a fallback match)
                programme = Programme.objects.filter(
                    name__iexact=entry.get("category", entry["programme_name"])
                ).first()

                if not programme:
                    skipped.append(f"{code} - {entry['programme_name']} at {entry['institution']} (no parent programme)")
                    continue

                offering = ProgrammeOffering.objects.create(
                    programme=programme,
                    institution=institution,
                    programme_code=code,
                    programme_name=entry["programme_name"],
                )
                offering_lookup[code] = offering
                created_offerings += 1

            cutoffs = entry.get("cutoffs", {})
            DegreeCutoff.objects.update_or_create(
                offering=offering,
                defaults={
                    "rank": entry["rank"],
                    "category": entry.get("category", ""),
                    "cutoff_2018": to_decimal(cutoffs.get("2018")),
                    "cutoff_2019": to_decimal(cutoffs.get("2019")),
                    "cutoff_2020": to_decimal(cutoffs.get("2020")),
                    "cutoff_2021": to_decimal(cutoffs.get("2021")),
                    "cutoff_2022": to_decimal(cutoffs.get("2022")),
                    "cutoff_2023": to_decimal(cutoffs.get("2023")),
                    "cutoff_2024": to_decimal(cutoffs.get("2024")),
                },
            )
            created_cutoffs += 1

        if skipped:
            self.stdout.write(self.style.WARNING(f"Skipped {len(skipped)} entries:"))
            for s in skipped:
                self.stdout.write(f"  - {s}")

        if created_offerings:
            self.stdout.write(f"Created {created_offerings} new programme offerings.")

        self.stdout.write(
            self.style.SUCCESS(f"Imported {created_cutoffs} degree cutoff records.")
        )
