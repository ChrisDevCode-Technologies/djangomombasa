from django.core.management.base import BaseCommand
from django.utils import timezone

from membership.models import Member

from events_and_activities.models import (
    Event,
    RSVP,
    ScheduleSlot,
    SpeakerProposal,
    Tag,
    VolunteerSignup,
)


MEMBERS = [
    {
        'name': 'Alice Kamau',
        'email': 'alice.kamau@example.com',
        'phone': '+254 700 111 222',
        'gender': Member.Gender.FEMALE,
        'year_of_birth': 1994,
        'experience_level': Member.ExperienceLevel.MID,
        'primary_language': Member.PrimaryLanguage.PYTHON,
    },
    {
        'name': 'Bob Otieno',
        'email': 'bob.otieno@example.com',
        'phone': '+254 711 222 333',
        'gender': Member.Gender.MALE,
        'year_of_birth': 1990,
        'experience_level': Member.ExperienceLevel.SENIOR,
        'primary_language': Member.PrimaryLanguage.GO,
    },
    {
        'name': 'Carol Wanjiku',
        'email': 'carol.wanjiku@example.com',
        'phone': '+254 722 333 444',
        'gender': Member.Gender.FEMALE,
        'year_of_birth': 2000,
        'experience_level': Member.ExperienceLevel.JUNIOR,
        'primary_language': Member.PrimaryLanguage.JAVASCRIPT,
    },
]


class Command(BaseCommand):
    help = 'Seed demo data for the events_and_activities app (events, RSVPs, speaker proposals, volunteer signups). Idempotent.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete demo events and their submissions before re-seeding (members are preserved).',
        )

    def handle(self, *args, **options):
        now = timezone.now()

        if options['reset']:
            deleted, _ = Event.objects.filter(
                name__in=[
                    'Demo: Async Django Workshop',
                    'Demo: External RSVP Meetup',
                    'Demo: Past Hack Night',
                ]
            ).delete()
            self.stdout.write(self.style.WARNING(f'Deleted {deleted} demo Event rows (cascaded RSVPs/proposals/signups).'))

        members = self._seed_members()
        tags = self._seed_tags()
        events = self._seed_events(now, tags)
        self._seed_submissions(events, members)

        self.stdout.write(self.style.SUCCESS('\nDemo data ready. Try these URLs:'))
        for ev in events.values():
            self.stdout.write(f'  /event/{ev.slug}/')
        self.stdout.write('\nAdmin: /dashboard/')

    def _seed_members(self):
        created = []
        members = {}
        for data in MEMBERS:
            member, was_created = Member.objects.get_or_create(
                email=data['email'],
                defaults=data,
            )
            members[data['email']] = member
            if was_created:
                created.append(member)
        self.stdout.write(self.style.SUCCESS(
            f'Members: {len(members)} total ({len(created)} new). '
            f'IDs: {", ".join(m.member_id for m in members.values())}'
        ))
        return members

    def _seed_tags(self):
        names = ['Backend', 'Beginner-friendly', 'Hands-on']
        tags = {}
        for name in names:
            tag, _ = Tag.objects.get_or_create(name=name)
            tags[name] = tag
        self.stdout.write(self.style.SUCCESS(f'Tags: {", ".join(tags.keys())}'))
        return tags

    def _seed_events(self, now, tags):
        specs = [
            {
                'name': 'Demo: Async Django Workshop',
                'date': now + timezone.timedelta(days=14),
                'details': (
                    'A hands-on workshop covering async views, async ORM, and '
                    'how to wire up background tasks in Django.\n\n'
                    'Bring a laptop with Python 3.12+ and Django 6 installed.'
                ),
                'rsvp_link': '',
                'has_rsvp': True,
                'has_cfp': True,
                'has_cfv': True,
                'rsvp_capacity': 5,
                'rsvp_deadline': now + timezone.timedelta(days=12),
                'tags': ['Backend', 'Hands-on'],
            },
            {
                'name': 'Demo: External RSVP Meetup',
                'date': now + timezone.timedelta(days=21),
                'details': 'A regular community meetup. RSVPs are handled via Luma.',
                'rsvp_link': 'https://example.com/external-rsvp',
                'has_rsvp': False,
                'has_cfp': False,
                'has_cfv': False,
                'tags': ['Beginner-friendly'],
            },
            {
                'name': 'Demo: Past Hack Night',
                'date': now - timezone.timedelta(days=10),
                'details': 'Looking back on our recent hack night.',
                'rsvp_link': '',
                'has_rsvp': False,
                'has_cfp': False,
                'has_cfv': False,
                'tags': ['Hands-on'],
            },
        ]

        events = {}
        for spec in specs:
            tag_names = spec.pop('tags')
            event, was_created = Event.objects.get_or_create(
                name=spec['name'],
                defaults=spec,
            )
            if not was_created:
                for field, value in spec.items():
                    setattr(event, field, value)
                event.save()
            event.tags.set([tags[n] for n in tag_names])
            events[spec['name']] = event
            verb = 'Created' if was_created else 'Updated'
            self.stdout.write(self.style.SUCCESS(
                f'{verb} event: {event.name} (slug={event.slug}, '
                f'has_rsvp={event.has_rsvp}, has_cfp={event.has_cfp}, has_cfv={event.has_cfv})'
            ))
        return events

    def _seed_submissions(self, events, members):
        workshop = events['Demo: Async Django Workshop']

        rsvp_pairs = [
            ('alice.kamau@example.com', workshop),
            ('bob.otieno@example.com', workshop),
        ]
        rsvp_created = 0
        for email, event in rsvp_pairs:
            _, was_created = RSVP.objects.get_or_create(event=event, member=members[email])
            rsvp_created += int(was_created)
        self.stdout.write(self.style.SUCCESS(
            f'RSVPs for "{workshop.name}": {len(rsvp_pairs)} total ({rsvp_created} new).'
        ))

        proposals = [
            {
                'name': 'Dana Migwi',
                'email': 'dana.migwi@example.com',
                'proposed_talk_title': 'Async Django in production',
                'talk_abstract': 'A look at how we migrated a large Django app to async views and what broke along the way.',
                'bio': 'Backend engineer, Nairobi.',
                'status': SpeakerProposal.Status.PENDING,
            },
            {
                'name': 'Eli Mwangi',
                'email': 'eli.mwangi@example.com',
                'proposed_talk_title': 'Background tasks without Celery',
                'talk_abstract': 'How to use Django 6 + asyncio to run lightweight background jobs without pulling in Celery or Redis.',
                'bio': '',
                'status': SpeakerProposal.Status.APPROVED,
            },
        ]
        prop_created = 0
        for spec in proposals:
            _, was_created = SpeakerProposal.objects.get_or_create(
                event=workshop,
                email=spec['email'],
                proposed_talk_title=spec['proposed_talk_title'],
                defaults=spec,
            )
            prop_created += int(was_created)
        self.stdout.write(self.style.SUCCESS(
            f'Speaker proposals for "{workshop.name}": {len(proposals)} total ({prop_created} new).'
        ))

        signups = [
            {
                'name': 'Faith Nyambura',
                'email': 'faith.nyambura@example.com',
                'phone': '+254 733 444 555',
                'availability': 'Available the full day, including setup.',
                'skills_or_role': 'Registration desk + photography',
                'status': VolunteerSignup.Status.PENDING,
            },
            {
                'name': 'George Kiprop',
                'email': 'george.kiprop@example.com',
                'phone': '',
                'availability': 'Afternoon only.',
                'skills_or_role': 'AV support',
                'status': VolunteerSignup.Status.APPROVED,
            },
        ]
        sign_created = 0
        for spec in signups:
            _, was_created = VolunteerSignup.objects.get_or_create(
                event=workshop,
                email=spec['email'],
                skills_or_role=spec['skills_or_role'],
                defaults=spec,
            )
            sign_created += int(was_created)
        self.stdout.write(self.style.SUCCESS(
            f'Volunteer signups for "{workshop.name}": {len(signups)} total ({sign_created} new).'
        ))

        approved_proposal = SpeakerProposal.objects.filter(
            event=workshop, status=SpeakerProposal.Status.APPROVED,
        ).first()

        schedule_specs = [
            {
                'order': 1,
                'title': 'Doors open + registration',
                'summary': 'Pick up your name tag and grab a coffee.',
                'speaker_proposal': None,
                'manual_speaker_name': '',
                'manual_speaker_bio': '',
            },
            {
                'order': 2,
                'title': 'Background tasks without Celery',
                'summary': 'Talk from an approved speaker proposal.',
                'speaker_proposal': approved_proposal,
                'manual_speaker_name': '',
                'manual_speaker_bio': '',
            },
            {
                'order': 3,
                'title': 'Guest keynote: Scaling Django on Africa-region infra',
                'summary': 'A guest speaker invited directly by the organizing team.',
                'speaker_proposal': None,
                'manual_speaker_name': 'Hawi Mbeti',
                'manual_speaker_bio': 'Cloud platform lead, organising committee Nairobi.',
            },
        ]
        slot_created = 0
        for spec in schedule_specs:
            _, was_created = ScheduleSlot.objects.get_or_create(
                event=workshop,
                title=spec['title'],
                defaults=spec,
            )
            slot_created += int(was_created)
        self.stdout.write(self.style.SUCCESS(
            f'Schedule slots for "{workshop.name}": {len(schedule_specs)} total ({slot_created} new).'
        ))
