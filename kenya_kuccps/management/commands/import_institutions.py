import html
import json
import sys

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from kenya_kuccps.models import (
    County,
    Institution,
    InstitutionCategory,
    InstitutionType,
    ParentMinistry,
)


class Command(BaseCommand):
    help = "Import KUCCPS institutions from a JSON file."

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            nargs="?",
            default="-",
            help="Path to JSON file (default: read from stdin)",
        )

    def handle(self, *args, **options):
        json_file = options["json_file"]

        if json_file == "-":
            data = json.load(sys.stdin)
        else:
            try:
                with open(json_file) as f:
                    data = json.load(f)
            except FileNotFoundError:
                raise CommandError(f"File not found: {json_file}")

        created = 0
        updated = 0
        skipped = 0

        with transaction.atomic():
            for entry in data:
                name = html.unescape(entry.get("name", "")).strip()
                category_name = entry.get("category", "").strip()
                type_name = entry.get("institution_type", "").strip()
                ministry_name = html.unescape(entry.get("parent_ministry", "")).strip()
                location = entry.get("location", "").strip()
                code = entry.get("key", "").strip()
                number = entry.get("number", "").strip()

                if not number or not code or not name:
                    self.stderr.write(
                        self.style.WARNING(f"  Skipped #{number}: missing required fields")
                    )
                    skipped += 1
                    continue

                if not category_name or not type_name or location in ("", "COUNTY"):
                    self.stderr.write(
                        self.style.WARNING(f"  Skipped #{number} ({code}): incomplete data")
                    )
                    skipped += 1
                    continue

                category, _ = InstitutionCategory.objects.get_or_create(name=category_name)
                inst_type, _ = InstitutionType.objects.get_or_create(name=type_name)
                county, _ = County.objects.get_or_create(name=location)

                if ministry_name:
                    ministry, _ = ParentMinistry.objects.get_or_create(name=ministry_name)
                else:
                    ministry, _ = ParentMinistry.objects.get_or_create(name="Unspecified")

                _, is_new = Institution.objects.update_or_create(
                    kuccps_number=int(number),
                    defaults={
                        "code": code,
                        "name": name,
                        "category": category,
                        "institution_type": inst_type,
                        "parent_ministry": ministry,
                        "county": county,
                    },
                )

                if is_new:
                    created += 1
                else:
                    updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done: {created} created, {updated} updated, {skipped} skipped "
                f"(total in file: {len(data)})"
            )
        )
