from django.db import models
from django.utils.text import slugify


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'app_tag'

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='events')
    date = models.DateTimeField()
    rsvp_link = models.URLField(blank=True)
    details = models.TextField()
    has_rsvp = models.BooleanField(
        default=False,
        help_text='Enable the internal members-only RSVP form. When off, the external rsvp_link is used instead.',
    )
    has_cfp = models.BooleanField(
        default=False,
        help_text='Enable the Call for Speakers section on the event detail page.',
    )
    has_cfv = models.BooleanField(
        default=False,
        help_text='Enable the Call for Volunteers section on the event detail page.',
    )

    class Meta:
        db_table = 'app_event'
        ordering = ['date']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            n = 1
            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class RSVP(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    member = models.ForeignKey('membership.Member', on_delete=models.CASCADE, related_name='event_rsvps')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'app_rsvp'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['event', 'member'], name='unique_event_member_rsvp'),
        ]

    def __str__(self):
        return f'{self.member.member_id} → {self.event.name}'


class SpeakerProposal(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='speaker_proposals')
    name = models.CharField(max_length=200)
    email = models.EmailField()
    proposed_talk_title = models.CharField(max_length=250)
    talk_abstract = models.TextField()
    bio = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'app_speaker_proposal'
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.name} — {self.proposed_talk_title} ({self.event.name})'


class VolunteerSignup(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='volunteer_signups')
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    availability = models.TextField()
    skills_or_role = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'app_volunteer_signup'
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.name} — {self.event.name}'
