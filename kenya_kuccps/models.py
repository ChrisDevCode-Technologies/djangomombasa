import uuid
from django.db import models


class County(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Counties"

    def __str__(self):
        return self.name


class ParentMinistry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    name = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name_plural = "Parent ministries"

    def __str__(self):
        return self.name


class InstitutionCategory(models.Model):
    # University / College
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Institution categories"

    def __str__(self):
        return self.name


class InstitutionType(models.Model):
    # Public / Private
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Institution types"

    def __str__(self):
        return self.name


class Institution(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    kuccps_number = models.PositiveIntegerField(unique=True)
    code = models.CharField(max_length=50, unique=True)  # e.g. AIU, KMTC - MOMBASA
    name = models.CharField(max_length=255)

    category = models.ForeignKey(
        InstitutionCategory,
        on_delete=models.PROTECT,
        related_name="institutions",
        null=True,
        blank=True,
    )

    institution_type = models.ForeignKey(
        InstitutionType,
        on_delete=models.PROTECT,
        related_name="institutions",
        null=True,
        blank=True,
    )

    parent_ministry = models.ForeignKey(
        ParentMinistry,
        on_delete=models.PROTECT,
        related_name="institutions",
        null=True,
        blank=True,
    )

    county = models.ForeignKey(
        County,
        on_delete=models.PROTECT,
        related_name="institutions",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
        ]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class ProgrammeGroup(models.Model):
    """Cluster / category grouping for programmes (e.g. 'Cluster 3 - Social Sciences...')."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Programme(models.Model):
    """A KUCCPS programme (e.g. 'BACHELOR OF ARTS')."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    kuccps_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Programme ID from KUCCPS (e.g. '1001').",
    )
    name = models.CharField(max_length=255, db_index=True)
    group = models.ForeignKey(
        ProgrammeGroup,
        on_delete=models.PROTECT,
        related_name="programmes",
    )
    detail_url = models.CharField(max_length=255, blank=True)
    cluster_requirements = models.JSONField(
        default=dict,
        blank=True,
        help_text="Cluster subject requirements, e.g. {'Cluster Subject 1': 'ENG / KIS', ...}",
    )
    subject_requirements = models.JSONField(
        default=dict,
        blank=True,
        help_text="Minimum subject requirements, e.g. {'Subject 1': 'MAT A', ...}",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.kuccps_id})"


class ProgrammeOffering(models.Model):
    """A specific programme offered at a specific institution, with cut-off points."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    programme = models.ForeignKey(
        Programme,
        on_delete=models.CASCADE,
        related_name="offerings",
    )
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name="programme_offerings",
    )
    programme_code = models.CharField(
        max_length=20,
        db_index=True,
        help_text="Institution-specific programme code (e.g. '1700201').",
    )
    programme_name = models.CharField(
        max_length=255,
        help_text="Programme name as offered at the institution.",
    )
    cutoff_2023 = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True,
        verbose_name="KCSE 2023 Cut-off",
    )
    cutoff_2024 = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True,
        verbose_name="KCSE 2024 Cut-off",
    )
    cutoff_2025 = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True,
        verbose_name="KCSE 2025 Cut-off",
    )

    class Meta:
        ordering = ["institution__name", "programme_name"]
        unique_together = [("programme", "programme_code")]

    def __str__(self):
        return f"{self.programme_name} at {self.institution}"


class DegreeCutoff(models.Model):
    """Historical degree programme cut-off points (2018–2024) from KUCCPS."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    offering = models.OneToOneField(
        ProgrammeOffering,
        on_delete=models.CASCADE,
        related_name="degree_cutoff",
    )
    rank = models.PositiveIntegerField(
        help_text="Rank within the programme category.",
    )
    category = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Programme category (e.g. 'BACHELOR OF ARTS').",
    )
    cutoff_2018 = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True,
        verbose_name="2018 Cut-off",
    )
    cutoff_2019 = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True,
        verbose_name="2019 Cut-off",
    )
    cutoff_2020 = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True,
        verbose_name="2020 Cut-off",
    )
    cutoff_2021 = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True,
        verbose_name="2021 Cut-off",
    )
    cutoff_2022 = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True,
        verbose_name="2022 Cut-off",
    )
    cutoff_2023 = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True,
        verbose_name="2023 Cut-off",
    )
    cutoff_2024 = models.DecimalField(
        max_digits=6, decimal_places=3, null=True, blank=True,
        verbose_name="2024 Cut-off",
    )

    class Meta:
        ordering = ["category", "rank"]

    def __str__(self):
        return f"{self.offering.programme_name} (rank {self.rank})"


class TvetSection(models.Model):
    """Examination section grouping for TVET programmes (e.g. 'KNEC Examination Programmes')."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class TvetRequirement(models.Model):
    """
    Minimum subject requirements for a TVET programme at a specific level.

    Each row represents one level (Diploma / Certificate / Artisan) of a
    programme category within an examination section.
    """

    LEVEL_CHOICES = [
        ("DIPLOMA", "Diploma"),
        ("CERTIFICATE", "Certificate"),
        ("ARTISAN", "Artisan"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    section = models.ForeignKey(
        TvetSection,
        on_delete=models.CASCADE,
        related_name="requirements",
    )
    number = models.PositiveIntegerField(
        help_text="Programme number within the section.",
    )
    category = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Programme category (e.g. 'Nursing', 'Engineering').",
    )
    subcategory = models.CharField(
        max_length=255,
        blank=True,
        help_text="Subcategory when applicable (e.g. 'Applied Biology' under Sciences).",
    )
    level = models.CharField(
        max_length=255,
        help_text="Qualification level as stated (e.g. 'Diploma', 'Diploma (Alternative A)').",
    )
    minimum_mean_grade = models.CharField(
        max_length=50,
        help_text="Minimum KCSE mean grade (e.g. 'C (plain)', 'D+').",
    )
    subject_requirements = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "Subject requirements — a list of strings, or a dict with named "
            "alternatives (e.g. {'science_based': [...], 'non_science_based': [...]})."
        ),
    )

    class Meta:
        ordering = ["section", "number", "category", "level"]

    def __str__(self):
        sub = f" — {self.subcategory}" if self.subcategory else ""
        return f"{self.category}{sub} ({self.level})"
