import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
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
    rsvp_deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Latest moment members can RSVP. Leave blank for no cutoff.',
    )
    rsvp_capacity = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Max number of RSVPs accepted. Leave blank for unlimited.',
    )
    reminder_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        help_text='When the day-before email reminder was last dispatched (set by the send_event_reminders command).',
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

    @property
    def rsvp_count(self):
        return self.rsvps.count()

    @property
    def rsvp_is_full(self):
        return self.rsvp_capacity is not None and self.rsvp_count >= self.rsvp_capacity

    @property
    def rsvp_deadline_passed(self):
        return self.rsvp_deadline is not None and self.rsvp_deadline < timezone.now()

    @property
    def rsvp_is_open(self):
        return self.has_rsvp and not self.rsvp_is_full and not self.rsvp_deadline_passed

    @property
    def rsvp_closed_reason(self):
        if self.rsvp_deadline_passed:
            return 'past_deadline'
        if self.rsvp_is_full:
            return 'full'
        return None

    @property
    def rsvp_seats_remaining(self):
        if self.rsvp_capacity is None:
            return None
        return max(self.rsvp_capacity - self.rsvp_count, 0)


class RSVP(models.Model):
    class CheckInStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        HELD = 'hold', 'On Hold'
        DENIED = 'denied', 'Denied'

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    member = models.ForeignKey('membership.Member', on_delete=models.CASCADE, related_name='event_rsvps')
    created_at = models.DateTimeField(auto_now_add=True)
    check_in_status = models.CharField(
        max_length=10,
        choices=CheckInStatus.choices,
        default=CheckInStatus.PENDING,
    )
    check_in_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'app_rsvp'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['event', 'member'], name='unique_event_member_rsvp'),
        ]

    def __str__(self):
        return f'{self.member.member_id} → {self.event.name}'

    def get_status_display(self):
        # Mirrors the speaker/volunteer pattern so the `_update_status` admin helper can read the label.
        return self.get_check_in_status_display()

    @property
    def email(self):
        # `_update_status` references instance.email when crafting status messages.
        return self.member.email


class SpeakerProposal(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        HOLD = 'hold', 'On Hold'

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
        HOLD = 'hold', 'On Hold'

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


class ScheduleSlot(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='schedule_slots')
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    speaker_proposal = models.ForeignKey(
        SpeakerProposal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='schedule_slots',
        limit_choices_to={'status': SpeakerProposal.Status.APPROVED},
        help_text='Pick an approved speaker proposal, or leave blank and fill the manual fields below.',
    )
    manual_speaker_name = models.CharField(max_length=200, blank=True)
    manual_speaker_bio = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'start_time', 'id']

    def clean(self):
        if self.speaker_proposal and self.manual_speaker_name:
            raise ValidationError('Pick a speaker proposal OR fill the manual speaker name, not both.')

    def __str__(self):
        return f'{self.event.name} · {self.title}'

    @property
    def speaker_display_name(self):
        if self.speaker_proposal:
            return self.speaker_proposal.name
        return self.manual_speaker_name or ''

    @property
    def speaker_display_bio(self):
        if self.speaker_proposal:
            return self.speaker_proposal.bio
        return self.manual_speaker_bio
