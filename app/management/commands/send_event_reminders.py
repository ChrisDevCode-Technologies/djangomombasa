"""
Email day-before reminders to everyone RSVP'd to events happening soon.

Designed to be run frequently (e.g. hourly via cron). Only sends one
reminder per event — the timestamp is recorded on Event.reminder_sent_at,
so re-runs are safe.
"""

from __future__ import annotations

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from app import emails as notifications
from events_and_activities.models import Event


class Command(BaseCommand):
    help = 'Send a one-day-before email reminder to members who RSVP\'d to upcoming events.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--window-hours',
            type=float,
            default=24.0,
            help='Send reminders for events starting within this many hours from now (default: 24).',
        )
        parser.add_argument(
            '--lead-hours',
            type=float,
            default=20.0,
            help='Only consider events that start at least this many hours from now (default: 20). '
                 'Keeps the window centred on ~24h before the event.',
        )
        parser.add_argument(
            '--resend',
            action='store_true',
            help='Re-send reminders even if reminder_sent_at is already set.',
        )
        parser.add_argument(
            '--event-slug',
            help='Only process a specific event by slug.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually delivering email.',
        )

    def handle(self, *args, **opts):
        now = timezone.now()
        window_start = now + timedelta(hours=opts['lead_hours'])
        window_end = now + timedelta(hours=opts['window_hours'])

        qs = Event.objects.filter(date__gte=window_start, date__lte=window_end)
        if opts.get('event_slug'):
            qs = qs.filter(slug=opts['event_slug'])
        if not opts['resend']:
            qs = qs.filter(reminder_sent_at__isnull=True)

        total_events = 0
        total_sent = 0
        for event in qs:
            rsvps = (
                event.rsvps.select_related('member').all()
            )
            recipients = [r.member for r in rsvps if r.member.email]
            if not recipients:
                self.stdout.write(f'[{event.slug}] no RSVPs with email; skipping')
                continue
            total_events += 1
            self.stdout.write(
                f'[{event.slug}] {"DRY RUN — would send" if opts["dry_run"] else "sending"} to {len(recipients)} recipient(s)'
            )
            if opts['dry_run']:
                continue
            sent = notifications.send_event_reminder(event, recipients)
            total_sent += sent
            event.reminder_sent_at = timezone.now()
            event.save(update_fields=['reminder_sent_at'])
            self.stdout.write(self.style.SUCCESS(f'[{event.slug}] sent {sent}/{len(recipients)}'))

        if not total_events:
            self.stdout.write('No events due for a reminder in the current window.')
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Done. Events processed: {total_events}. Emails delivered: {total_sent}.'
            ))
