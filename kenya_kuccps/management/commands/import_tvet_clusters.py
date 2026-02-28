import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from kenya_kuccps.models import TvetSection, TvetRequirement


class Command(BaseCommand):
    help = "Import TVET minimum subject requirements from a JSON file."

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            help="Path to the tvet_clusters.json file.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing TVET requirement data before importing.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        json_path = Path(options["json_file"])
        if not json_path.exists():
            self.stderr.write(self.style.ERROR(f"File not found: {json_path}"))
            return

        with open(json_path, "r") as f:
            data = json.load(f)

        sections_data = data.get("sections", [])
        if not sections_data:
            self.stderr.write(self.style.ERROR("No sections found in JSON."))
            return

        if options["clear"]:
            deleted_reqs = TvetRequirement.objects.all().delete()[0]
            deleted_secs = TvetSection.objects.all().delete()[0]
            self.stdout.write(
                f"Cleared {deleted_reqs} requirements, {deleted_secs} sections."
            )

        total_created = 0

        for section_data in sections_data:
            section, _ = TvetSection.objects.get_or_create(
                name=section_data["section"]
            )

            for prog in section_data.get("programmes", []):
                number = prog["number"]
                category = prog["category"]

                # Some programmes have subcategories (e.g. Sciences)
                subcategories = prog.get("subcategories")
                if subcategories:
                    for sub in subcategories:
                        total_created += self._create_levels(
                            section=section,
                            number=number,
                            category=category,
                            subcategory=sub["name"],
                            levels=sub["levels"],
                        )
                else:
                    total_created += self._create_levels(
                        section=section,
                        number=number,
                        category=category,
                        subcategory="",
                        levels=prog.get("levels", []),
                    )

        sections_count = TvetSection.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {total_created} requirements across {sections_count} sections."
            )
        )

    def _create_levels(self, section, number, category, subcategory, levels):
        """Create TvetRequirement records for each level. Returns count created."""
        created = 0
        for level_data in levels:
            _, was_created = TvetRequirement.objects.update_or_create(
                section=section,
                number=number,
                category=category,
                subcategory=subcategory,
                level=level_data["level"],
                defaults={
                    "minimum_mean_grade": level_data["minimum_mean_grade"],
                    "subject_requirements": level_data["subject_requirements"],
                },
            )
            created += 1
        return created
