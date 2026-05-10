from django.db import models, transaction


class MemberIdSequence(models.Model):
    """
    Singleton table to track the next member ID number.
    Uses select_for_update() for race-safe ID generation.
    """
    next_number = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'app_memberidsequence'
        verbose_name = 'Member ID Sequence'
        verbose_name_plural = 'Member ID Sequence'

    @classmethod
    def get_next_id(cls):
        """
        Atomically get and increment the next member ID.
        Returns a formatted member ID string (e.g., 'DM-042').
        """
        with transaction.atomic():
            # Lock the sequence row for update
            seq, created = cls.objects.select_for_update().get_or_create(
                pk=1,
                defaults={'next_number': 0}
            )
            current = seq.next_number
            seq.next_number = current + 1
            seq.save(update_fields=['next_number'])
        return f'DM-{current:03d}'


class Member(models.Model):
    class Gender(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'

    class ExperienceLevel(models.TextChoices):
        JUNIOR = 'junior', 'Junior'
        MID = 'mid', 'Mid'
        SENIOR = 'senior', 'Senior'
        FOR_FUN = 'for_fun', 'For Fun'

    class PrimaryLanguage(models.TextChoices):
        PYTHON = 'python', 'Python'
        JAVASCRIPT = 'javascript', 'JavaScript'
        TYPESCRIPT = 'typescript', 'TypeScript'
        JAVA = 'java', 'Java'
        CSHARP = 'csharp', 'C#'
        CPP = 'cpp', 'C++'
        C = 'c', 'C'
        GO = 'go', 'Go'
        RUST = 'rust', 'Rust'
        PHP = 'php', 'PHP'
        RUBY = 'ruby', 'Ruby'
        SWIFT = 'swift', 'Swift'
        KOTLIN = 'kotlin', 'Kotlin'
        DART = 'dart', 'Dart'
        R = 'r', 'R'
        SQL = 'sql', 'SQL'
        OTHER = 'other', 'Other'

    member_id = models.CharField(max_length=10, unique=True, editable=False, default='')
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=10, choices=Gender.choices)
    year_of_birth = models.PositiveSmallIntegerField(null=True, blank=True)
    experience_level = models.CharField(max_length=10, choices=ExperienceLevel.choices)
    primary_language = models.CharField(max_length=20, choices=PrimaryLanguage.choices)
    receive_regular_updates = models.BooleanField(default=False, help_text='Receive regular community updates')
    receive_email_communications = models.BooleanField(default=False, help_text='Receive email communications about events and announcements')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'app_member'

    def save(self, *args, **kwargs):
        if not self.member_id:
            self.member_id = MemberIdSequence.get_next_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.member_id} — {self.name}'
