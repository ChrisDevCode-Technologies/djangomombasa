import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from kenya_kuccps.models import (
    Institution, InstitutionType, County,
    ProgrammeGroup, Programme, ProgrammeOffering,
)


INSTITUTION_TYPE_MAP = {
    "PUBLIC": "Public",
    "PRIVATE": "Private",
    "Ministry of Education": "Public",
    "In Other Ministries": "Public",
}


def parse_cutoff(value):
    """Return a Decimal or None for a cut-off string like '22.194' or '-'."""
    if not value or value.strip() == "-":
        return None
    try:
        return Decimal(value.strip())
    except InvalidOperation:
        return None


def build_institution_lookup():
    """Build a dict mapping uppercased institution name -> Institution object."""
    return {inst.name.upper(): inst for inst in Institution.objects.select_related("institution_type")}


def match_institution(offering_name, lookup):
    """
    Match an offering institution name like 'AFRICA NAZARENE UNIVERSITY KAJIADO COUNTY'
    to an Institution record by checking if the institution name is a prefix.
    Returns (Institution, county_name) or (None, None).
    """
    offering_upper = offering_name.upper()
    for inst_name, inst in lookup.items():
        if offering_upper.startswith(inst_name + " ") or offering_upper == inst_name:
            # Extract county name: everything after the institution name, minus ' COUNTY'
            remainder = offering_upper[len(inst_name):].strip()
            county_name = remainder.removesuffix(" COUNTY").strip() if remainder else None
            return inst, county_name
    return None, None


def extract_institution_name_and_county(offering_name):
    """
    For unmatched institutions, extract a plausible name and county from
    'INSTITUTION NAME COUNTY_NAME COUNTY'.
    """
    upper = offering_name.upper().strip()
    if upper.endswith(" COUNTY"):
        # Find the last word before 'COUNTY' that could be a county name
        without_county = upper.removesuffix(" COUNTY").strip()
        # Split and try to find where county name starts
        # County names in the offering are typically 1-2 words before COUNTY
        words = without_county.split()
        # Try 2-word county name, then 1-word
        for county_len in (2, 1):
            if len(words) > county_len:
                county_name = " ".join(words[-county_len:])
                inst_name = " ".join(words[:-county_len])
                if inst_name:
                    return inst_name, county_name
    return upper, None


class Command(BaseCommand):
    help = "Import KUCCPS programmes from a JSON file."

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            help="Path to the kuccps_programmes.json file.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing programme data before importing.",
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
            deleted_offerings = ProgrammeOffering.objects.all().delete()[0]
            deleted_programmes = Programme.objects.all().delete()[0]
            deleted_groups = ProgrammeGroup.objects.all().delete()[0]
            self.stdout.write(
                f"Cleared {deleted_offerings} offerings, "
                f"{deleted_programmes} programmes, {deleted_groups} groups."
            )

        # Pass 1: collect unique groups and create them
        group_names = {p["group"] for p in programmes_data}
        group_objects = {}
        for name in group_names:
            obj, _ = ProgrammeGroup.objects.get_or_create(name=name)
            group_objects[name] = obj
        self.stdout.write(f"Groups: {len(group_objects)}")

        # Pass 2: create programmes
        programme_objects = {}
        for p in programmes_data:
            obj, created = Programme.objects.update_or_create(
                kuccps_id=p["id"],
                defaults={
                    "name": p["name"],
                    "group": group_objects[p["group"]],
                    "detail_url": p.get("detail_url", ""),
                    "cluster_requirements": p.get("cluster_requirements", {}),
                    "subject_requirements": p.get("subject_requirements", {}),
                },
            )
            programme_objects[p["id"]] = obj
        self.stdout.write(f"Programmes: {len(programme_objects)}")

        # Pass 3: build institution lookup and resolve offerings
        inst_lookup = build_institution_lookup()
        institution_cache = {}  # offering institution name -> Institution
        unmatched = set()
        created_count = 0

        # Collect all unique offering institution names first
        all_offering_names = set()
        for p in programmes_data:
            for o in p.get("offerings", []):
                all_offering_names.add(o["Institution"])

        # Resolve each to an Institution
        for offering_name in all_offering_names:
            inst, county_name = match_institution(offering_name, inst_lookup)
            if inst:
                institution_cache[offering_name] = inst
            else:
                # Create missing institution
                inst_name, county_name = extract_institution_name_and_county(offering_name)
                # Title-case for consistency
                inst_name_titled = inst_name.title()

                county = None
                if county_name:
                    county, _ = County.objects.get_or_create(
                        name=county_name.title()
                    )

                inst_type, _ = InstitutionType.objects.get_or_create(name="Public")

                # Generate a unique kuccps_number for new institutions
                max_num = Institution.objects.order_by("-kuccps_number").values_list(
                    "kuccps_number", flat=True
                ).first() or 0

                inst = Institution.objects.create(
                    kuccps_number=max_num + 1,
                    code=inst_name_titled[:50],
                    name=inst_name_titled,
                    institution_type=inst_type,
                    county=county,
                )
                # Add to lookup so subsequent offerings match
                inst_lookup[inst.name.upper()] = inst
                institution_cache[offering_name] = inst
                unmatched.add(offering_name)
                created_count += 1

        if unmatched:
            self.stdout.write(
                self.style.WARNING(
                    f"Created {created_count} new institutions for unmatched names:"
                )
            )
            for name in sorted(unmatched):
                self.stdout.write(f"  - {name}")

        # Pass 4: bulk-create offerings
        offerings_to_create = []
        seen_keys = set()

        for p in programmes_data:
            programme = programme_objects[p["id"]]
            for o in p.get("offerings", []):
                code = o["Programme Code"]
                key = (programme.pk, code)
                if key in seen_keys:
                    continue
                seen_keys.add(key)

                inst = institution_cache[o["Institution"]]

                offerings_to_create.append(
                    ProgrammeOffering(
                        programme=programme,
                        institution=inst,
                        programme_code=code,
                        programme_name=o["Programme Name"],
                        cutoff_2023=parse_cutoff(o.get("KCSE 2023 Cut-off")),
                        cutoff_2024=parse_cutoff(o.get("KCSE 2024 Cut-off")),
                        cutoff_2025=parse_cutoff(o.get("KCSE 2025 Cut-off")),
                    )
                )

        # Delete existing offerings if not using --clear (idempotent re-import)
        if not options["clear"]:
            ProgrammeOffering.objects.filter(
                programme__in=programme_objects.values()
            ).delete()

        ProgrammeOffering.objects.bulk_create(offerings_to_create, batch_size=1000)
        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {len(offerings_to_create)} offerings across "
                f"{len(programme_objects)} programmes in {len(group_objects)} groups."
            )
        )
