from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models import Organizer, Page, Partner, SocialLink, Sponsor
from blog_and_news.models import Article, NewsItem, Topic
from events_and_activities.models import (
    Event,
    RSVP,
    ScheduleSlot,
    SpeakerProposal,
    Tag,
    VolunteerSignup,
)
from membership.models import Member, RSVPGuest


MEMBERS = [
    {
        'name': 'Alice Kamau',
        'email': 'alice.kamau@example.com',
        'phone': '+254 700 111 222',
        'gender': Member.Gender.FEMALE,
        'year_of_birth': 1994,
        'experience_level': Member.ExperienceLevel.MID,
        'primary_language': Member.PrimaryLanguage.PYTHON,
        'receive_regular_updates': True,
        'receive_email_communications': True,
    },
    {
        'name': 'Bob Otieno',
        'email': 'bob.otieno@example.com',
        'phone': '+254 711 222 333',
        'gender': Member.Gender.MALE,
        'year_of_birth': 1990,
        'experience_level': Member.ExperienceLevel.SENIOR,
        'primary_language': Member.PrimaryLanguage.GO,
        'receive_regular_updates': True,
        'receive_email_communications': False,
    },
    {
        'name': 'Carol Wanjiku',
        'email': 'carol.wanjiku@example.com',
        'phone': '+254 722 333 444',
        'gender': Member.Gender.FEMALE,
        'year_of_birth': 2000,
        'experience_level': Member.ExperienceLevel.JUNIOR,
        'primary_language': Member.PrimaryLanguage.JAVASCRIPT,
        'receive_regular_updates': False,
        'receive_email_communications': True,
    },
    {
        'name': 'David Mwema',
        'email': 'david.mwema@example.com',
        'phone': '+254 733 555 666',
        'gender': Member.Gender.MALE,
        'year_of_birth': 1988,
        'experience_level': Member.ExperienceLevel.FOR_FUN,
        'primary_language': Member.PrimaryLanguage.RUST,
        'receive_regular_updates': False,
        'receive_email_communications': False,
    },
    {
        'name': 'Esther Njoki',
        'email': 'esther.njoki@example.com',
        'phone': '+254 744 666 777',
        'gender': Member.Gender.FEMALE,
        'year_of_birth': 1996,
        'experience_level': Member.ExperienceLevel.MID,
        'primary_language': Member.PrimaryLanguage.TYPESCRIPT,
        'receive_regular_updates': True,
        'receive_email_communications': True,
    },
    {
        'name': 'Frank Owino',
        'email': 'frank.owino@example.com',
        'phone': '',
        'gender': None,
        'year_of_birth': None,
        'experience_level': None,
        'primary_language': None,
        'receive_regular_updates': False,
        'receive_email_communications': False,
    },
    {
        'name': 'Grace Atieno',
        'email': 'grace.atieno@example.com',
        'phone': '+254 755 777 888',
        'gender': Member.Gender.FEMALE,
        'year_of_birth': 1998,
        'experience_level': Member.ExperienceLevel.SENIOR,
        'primary_language': Member.PrimaryLanguage.JAVA,
        'receive_regular_updates': True,
        'receive_email_communications': True,
    },
    {
        'name': 'Henry Mutua',
        'email': 'henry.mutua@example.com',
        'phone': '+254 766 888 999',
        'gender': Member.Gender.MALE,
        'year_of_birth': 1992,
        'experience_level': Member.ExperienceLevel.JUNIOR,
        'primary_language': Member.PrimaryLanguage.PHP,
        'receive_regular_updates': True,
        'receive_email_communications': True,
    },
    {
        'name': 'Ivy Chebet',
        'email': 'ivy.chebet@example.com',
        'phone': '+254 777 999 000',
        'gender': Member.Gender.FEMALE,
        'year_of_birth': 2002,
        'experience_level': Member.ExperienceLevel.JUNIOR,
        'primary_language': Member.PrimaryLanguage.OTHER,
        'receive_regular_updates': True,
        'receive_email_communications': True,
    },
]


# Guests stored in the same table via the RSVPGuest proxy (kind='rsvp_guest').
RSVP_GUESTS = [
    {
        'name': 'Jane Visitor',
        'email': 'jane.visitor@example.com',
        'phone': '+254 700 000 001',
    },
    {
        'name': 'Kevin Walkin',
        'email': 'kevin.walkin@example.com',
        'phone': '',
    },
]


DEMO_EVENT_NAMES = [
    'Demo: Async Django Workshop',
    'Demo: External RSVP Meetup',
    'Demo: Past Hack Night',
    'Demo: Multi-day Coastal Conference',
    'Demo: Full Capacity Meetup',
    'Demo: Closed RSVP & CFP Summit',
]


class Command(BaseCommand):
    help = (
        'Seed demo data across all apps: accounts, app (pages, organizers, partners, '
        'sponsors, social links), blog_and_news (topics, articles, news items), '
        'events_and_activities (tags, events, RSVPs, speaker proposals, volunteer signups), '
        'and membership (members). Idempotent.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete demo events and their submissions before re-seeding (members and other data are preserved).',
        )

    def handle(self, *args, **options):
        now = timezone.now()

        if options['reset']:
            deleted, _ = Event.objects.filter(name__in=DEMO_EVENT_NAMES).delete()
            self.stdout.write(self.style.WARNING(
                f'Deleted {deleted} demo Event rows (cascaded RSVPs/proposals/signups).'
            ))

        self._seed_users()
        members = self._seed_members()
        self._seed_rsvp_guests()
        tags = self._seed_tags()
        events = self._seed_events(now, tags)
        self._seed_submissions(events, members)
        self._seed_schedule_slots(now, events)
        organizers = self._seed_organizers()
        self._seed_partners(events)
        self._seed_sponsors(events)
        self._seed_social_links()
        self._seed_pages()
        topics = self._seed_topics()
        self._seed_articles(now, organizers, topics)
        self._seed_news_items(now, events, topics)

        self.stdout.write(self.style.SUCCESS('\nDemo data ready. Try these URLs:'))
        for ev in events.values():
            self.stdout.write(f'  /event/{ev.slug}/')
        self.stdout.write('\nAdmin: /dashboard/')

    def _seed_users(self):
        User = get_user_model()
        user_specs = [
            {'email': 'member@mail.com', 'is_staff': False, 'is_superuser': False, 'password': 'memberpass123'},
            {'email': 'staff@mail.com', 'is_staff': True, 'is_superuser': False, 'password': 'staffpass123'},
            {'email': 'admin@mail.com', 'is_staff': True, 'is_superuser': True, 'password': 'adminpass123'},
        ]
        for spec in user_specs:
            password = spec.pop('password')
            user, was_created = User.objects.get_or_create(
                email=spec['email'],
                defaults={'is_staff': spec['is_staff'], 'is_superuser': spec['is_superuser']},
            )
            # Always (re)apply the demo password and flags so credentials are predictable on re-run.
            user.is_staff = spec['is_staff']
            user.is_superuser = spec['is_superuser']
            user.set_password(password)
            user.save()
            verb = 'Created' if was_created else 'Updated'
            self.stdout.write(self.style.SUCCESS(
                f'User: {verb} {spec["email"]} / password={password} '
                f'(staff={spec["is_staff"]}, super={spec["is_superuser"]})'
            ))

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

    def _seed_rsvp_guests(self):
        created = 0
        for data in RSVP_GUESTS:
            _, was_created = RSVPGuest.objects.get_or_create(
                email=data['email'],
                defaults={
                    'name': data['name'],
                    'phone': data['phone'],
                    'kind': Member.Kind.RSVP_GUEST,
                },
            )
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(
            f'RSVP guests: {len(RSVP_GUESTS)} total ({created} new).'
        ))

    def _seed_tags(self):
        names = ['Backend', 'Beginner-friendly', 'Hands-on', 'Frontend', 'DevOps']
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
                'end_date': None,
                'details': (
                    'A hands-on workshop covering async views, async ORM, and '
                    'how to wire up background tasks in Django.\n\n'
                    'Bring a laptop with Python 3.12+ and Django 6 installed.'
                ),
                'rsvp_link': '',
                'has_rsvp': True,
                'has_cfp': True,
                'has_cfv': True,
                'rsvp_capacity': 10,
                'rsvp_deadline': now + timezone.timedelta(days=12),
                'cfp_deadline': now + timezone.timedelta(days=7),
                'cfv_deadline': now + timezone.timedelta(days=10),
                'tags': ['Backend', 'Hands-on'],
            },
            {
                'name': 'Demo: External RSVP Meetup',
                'date': now + timezone.timedelta(days=21),
                'end_date': None,
                'details': 'A regular community meetup. RSVPs are handled via Luma.',
                'rsvp_link': 'https://example.com/external-rsvp',
                'has_rsvp': False,
                'has_cfp': False,
                'has_cfv': False,
                'rsvp_capacity': None,
                'rsvp_deadline': None,
                'cfp_deadline': None,
                'cfv_deadline': None,
                'tags': ['Beginner-friendly'],
            },
            {
                'name': 'Demo: Past Hack Night',
                'date': now - timezone.timedelta(days=10),
                'end_date': None,
                'details': 'Looking back on our recent hack night.',
                'rsvp_link': '',
                'has_rsvp': False,
                'has_cfp': False,
                'has_cfv': False,
                'rsvp_capacity': None,
                'rsvp_deadline': None,
                'cfp_deadline': None,
                'cfv_deadline': None,
                'tags': ['Hands-on'],
            },
            {
                # Multi-day event exercises `end_date` and `is_one_day=False`.
                'name': 'Demo: Multi-day Coastal Conference',
                'date': now + timezone.timedelta(days=45),
                'end_date': now + timezone.timedelta(days=47),
                'details': (
                    'Three-day coastal Django conference with talks, '
                    'workshops, and a community day.'
                ),
                'rsvp_link': '',
                'has_rsvp': True,
                'has_cfp': True,
                'has_cfv': True,
                'rsvp_capacity': 100,
                'rsvp_deadline': now + timezone.timedelta(days=40),
                'cfp_deadline': now + timezone.timedelta(days=20),
                'cfv_deadline': now + timezone.timedelta(days=35),
                'tags': ['Backend', 'Frontend', 'DevOps'],
            },
            {
                # Capacity=3 with 3 RSVPs seeded below → exercises `rsvp_is_full`.
                'name': 'Demo: Full Capacity Meetup',
                'date': now + timezone.timedelta(days=5),
                'end_date': None,
                'details': 'Small-room meetup. Limited seats.',
                'rsvp_link': '',
                'has_rsvp': True,
                'has_cfp': False,
                'has_cfv': False,
                'rsvp_capacity': 3,
                'rsvp_deadline': now + timezone.timedelta(days=4),
                'cfp_deadline': None,
                'cfv_deadline': None,
                'tags': ['Beginner-friendly'],
            },
            {
                # All deadlines in the past → exercises `rsvp_deadline_passed`,
                # `cfp_deadline_passed`, and `cfv_deadline_passed`.
                'name': 'Demo: Closed RSVP & CFP Summit',
                'date': now + timezone.timedelta(days=2),
                'end_date': None,
                'details': 'Submissions and RSVPs are now closed.',
                'rsvp_link': '',
                'has_rsvp': True,
                'has_cfp': True,
                'has_cfv': True,
                'rsvp_capacity': 50,
                'rsvp_deadline': now - timezone.timedelta(days=1),
                'cfp_deadline': now - timezone.timedelta(days=5),
                'cfv_deadline': now - timezone.timedelta(days=2),
                'tags': ['DevOps'],
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
        conference = events['Demo: Multi-day Coastal Conference']
        full_meetup = events['Demo: Full Capacity Meetup']

        now = timezone.now()
        # Workshop RSVPs cover every check-in status, including a checked-in attendee.
        workshop_rsvp_specs = [
            {
                'email': 'alice.kamau@example.com',
                'check_in_status': RSVP.CheckInStatus.ACCEPTED,
                'checked_in_at': now - timezone.timedelta(hours=1),
            },
            {
                'email': 'bob.otieno@example.com',
                'check_in_status': RSVP.CheckInStatus.PENDING,
                'checked_in_at': None,
            },
            {
                'email': 'carol.wanjiku@example.com',
                'check_in_status': RSVP.CheckInStatus.HELD,
                'checked_in_at': None,
            },
            {
                'email': 'david.mwema@example.com',
                'check_in_status': RSVP.CheckInStatus.DENIED,
                'checked_in_at': None,
            },
        ]
        workshop_created = 0
        for spec in workshop_rsvp_specs:
            _, was_created = RSVP.objects.get_or_create(
                event=workshop,
                member=members[spec['email']],
                defaults={
                    'check_in_status': spec['check_in_status'],
                    'checked_in_at': spec['checked_in_at'],
                },
            )
            workshop_created += int(was_created)
        self.stdout.write(self.style.SUCCESS(
            f'RSVPs for "{workshop.name}": {len(workshop_rsvp_specs)} total ({workshop_created} new) '
            f'(covers all check-in statuses).'
        ))

        # Fill the small-capacity event to exercise `rsvp_is_full`.
        full_meetup_emails = [
            'esther.njoki@example.com',
            'grace.atieno@example.com',
            'henry.mutua@example.com',
        ]
        full_created = 0
        for email in full_meetup_emails:
            _, was_created = RSVP.objects.get_or_create(
                event=full_meetup,
                member=members[email],
                defaults={'check_in_status': RSVP.CheckInStatus.ACCEPTED},
            )
            full_created += int(was_created)
        self.stdout.write(self.style.SUCCESS(
            f'RSVPs for "{full_meetup.name}": {len(full_meetup_emails)} total ({full_created} new) '
            f'(capacity={full_meetup.rsvp_capacity}, is_full={full_meetup.rsvp_is_full}).'
        ))

        # A couple of RSVPs on the conference so its `rsvp_count` is non-zero.
        conference_emails = ['ivy.chebet@example.com', 'alice.kamau@example.com']
        conf_created = 0
        for email in conference_emails:
            _, was_created = RSVP.objects.get_or_create(
                event=conference,
                member=members[email],
                defaults={'check_in_status': RSVP.CheckInStatus.PENDING},
            )
            conf_created += int(was_created)
        self.stdout.write(self.style.SUCCESS(
            f'RSVPs for "{conference.name}": {len(conference_emails)} total ({conf_created} new).'
        ))

        # Speaker proposals: cover all four statuses across workshop + conference.
        proposals = [
            {
                'event': workshop,
                'name': 'Dana Migwi',
                'email': 'dana.migwi@example.com',
                'proposed_talk_title': 'Async Django in production',
                'talk_abstract': 'A look at how we migrated a large Django app to async views and what broke along the way.',
                'bio': 'Backend engineer, Nairobi.',
                'status': SpeakerProposal.Status.PENDING,
            },
            {
                'event': workshop,
                'name': 'Eli Mwangi',
                'email': 'eli.mwangi@example.com',
                'proposed_talk_title': 'Background tasks without Celery',
                'talk_abstract': 'How to use Django 6 + asyncio to run lightweight background jobs without pulling in Celery or Redis.',
                'bio': '',
                'status': SpeakerProposal.Status.APPROVED,
            },
            {
                'event': workshop,
                'name': 'Mary Wairimu',
                'email': 'mary.wairimu@example.com',
                'proposed_talk_title': 'A philosophical history of ORMs',
                'talk_abstract': 'Off-topic deep-dive — kept here to exercise the rejected pipeline.',
                'bio': 'Database historian.',
                'status': SpeakerProposal.Status.REJECTED,
            },
            {
                'event': workshop,
                'name': 'Noel Karanja',
                'email': 'noel.karanja@example.com',
                'proposed_talk_title': 'Django Channels deep-dive',
                'talk_abstract': 'A pragmatic guide to deploying Django Channels in production.',
                'bio': 'Realtime systems engineer.',
                'status': SpeakerProposal.Status.HOLD,
            },
            {
                'event': conference,
                'name': 'Olive Wambui',
                'email': 'olive.wambui@example.com',
                'proposed_talk_title': 'Patterns for multi-tenant Django',
                'talk_abstract': 'Lessons learned operating multi-tenant SaaS on Django.',
                'bio': 'Platform engineer.',
                'status': SpeakerProposal.Status.APPROVED,
            },
        ]
        prop_created = 0
        for spec in proposals:
            event_obj = spec.pop('event')
            _, was_created = SpeakerProposal.objects.get_or_create(
                event=event_obj,
                email=spec['email'],
                proposed_talk_title=spec['proposed_talk_title'],
                defaults=spec,
            )
            prop_created += int(was_created)
        self.stdout.write(self.style.SUCCESS(
            f'Speaker proposals: {len(proposals)} total ({prop_created} new) — covers PENDING/APPROVED/REJECTED/HOLD.'
        ))

        # Volunteer signups: cover all four statuses on the workshop.
        signups = [
            {
                'event': workshop,
                'name': 'Faith Nyambura',
                'email': 'faith.nyambura@example.com',
                'phone': '+254 733 444 555',
                'availability': 'Available the full day, including setup.',
                'skills_or_role': 'Registration desk + photography',
                'status': VolunteerSignup.Status.PENDING,
            },
            {
                'event': workshop,
                'name': 'George Kiprop',
                'email': 'george.kiprop@example.com',
                'phone': '',
                'availability': 'Afternoon only.',
                'skills_or_role': 'AV support',
                'status': VolunteerSignup.Status.APPROVED,
            },
            {
                'event': workshop,
                'name': 'Pauline Kerubo',
                'email': 'pauline.kerubo@example.com',
                'phone': '+254 700 222 333',
                'availability': 'Only available remotely.',
                'skills_or_role': 'Remote moderation',
                'status': VolunteerSignup.Status.REJECTED,
            },
            {
                'event': workshop,
                'name': 'Quincy Okoth',
                'email': 'quincy.okoth@example.com',
                'phone': '+254 700 333 444',
                'availability': 'Subject to my work shift; will confirm closer to the date.',
                'skills_or_role': 'Logistics',
                'status': VolunteerSignup.Status.HOLD,
            },
        ]
        sign_created = 0
        for spec in signups:
            event_obj = spec.pop('event')
            _, was_created = VolunteerSignup.objects.get_or_create(
                event=event_obj,
                email=spec['email'],
                skills_or_role=spec['skills_or_role'],
                defaults=spec,
            )
            sign_created += int(was_created)
        self.stdout.write(self.style.SUCCESS(
            f'Volunteer signups: {len(signups)} total ({sign_created} new) — covers PENDING/APPROVED/REJECTED/HOLD.'
        ))

    def _seed_schedule_slots(self, now, events):
        workshop = events['Demo: Async Django Workshop']
        approved_proposal = SpeakerProposal.objects.filter(
            event=workshop, status=SpeakerProposal.Status.APPROVED,
        ).first()

        # Anchor schedule times to the workshop date so durations render correctly.
        base = workshop.date.replace(hour=9, minute=0, second=0, microsecond=0)

        schedule_specs = [
            {
                'order': 1,
                'title': 'Doors open + registration',
                'summary': 'Pick up your name tag and grab a coffee.',
                'start_time': base,
                'end_time': base + timezone.timedelta(minutes=30),
                'speaker_proposal': None,
                'manual_speaker_name': '',
                'manual_speaker_bio': '',
            },
            {
                'order': 2,
                'title': 'Background tasks without Celery',
                'summary': 'Talk from an approved speaker proposal.',
                'start_time': base + timezone.timedelta(minutes=30),
                'end_time': base + timezone.timedelta(minutes=90),
                'speaker_proposal': approved_proposal,
                'manual_speaker_name': '',
                'manual_speaker_bio': '',
            },
            {
                'order': 3,
                'title': 'Guest keynote: Scaling Django on Africa-region infra',
                'summary': 'A guest speaker invited directly by the organizing team.',
                'start_time': base + timezone.timedelta(minutes=90),
                'end_time': base + timezone.timedelta(minutes=180),
                'speaker_proposal': None,
                'manual_speaker_name': 'Hawi Mbeti',
                'manual_speaker_bio': 'Cloud platform lead, organising committee Nairobi.',
            },
            {
                'order': 4,
                'title': 'Lunch break',
                'summary': 'Networking over lunch.',
                'start_time': None,
                'end_time': None,
                'speaker_proposal': None,
                'manual_speaker_name': '',
                'manual_speaker_bio': '',
            },
        ]
        slot_created = 0
        for spec in schedule_specs:
            slot, was_created = ScheduleSlot.objects.get_or_create(
                event=workshop,
                title=spec['title'],
                defaults=spec,
            )
            if not was_created:
                for field, value in spec.items():
                    setattr(slot, field, value)
                slot.save()
            slot_created += int(was_created)
        self.stdout.write(self.style.SUCCESS(
            f'Schedule slots for "{workshop.name}": {len(schedule_specs)} total ({slot_created} new).'
        ))

    def _seed_organizers(self):
        specs = [
            {
                'first_name': 'Hellen',
                'last_name': 'Achieng',
                'community_role': 'Lead Organizer',
                'professional_role': 'Senior Backend Engineer',
                'location': 'Mombasa, Kenya',
                'github_url': 'https://github.com/example-hellen',
                'linkedin_url': 'https://linkedin.com/in/example-hellen',
                'twitter_url': '',
                'website_url': '',
                'order': 1,
            },
            {
                'first_name': 'Ian',
                'last_name': 'Mutiso',
                'community_role': 'Events & Logistics',
                'professional_role': 'Full-stack Developer',
                'location': 'Mombasa, Kenya',
                'github_url': 'https://github.com/example-ian',
                'linkedin_url': '',
                'twitter_url': 'https://twitter.com/example-ian',
                'website_url': '',
                'order': 2,
            },
            {
                'first_name': 'Joy',
                'last_name': 'Akoth',
                'community_role': 'Community Manager',
                'professional_role': 'Developer Advocate',
                'location': 'Kilifi, Kenya',
                'github_url': '',
                'linkedin_url': 'https://linkedin.com/in/example-joy',
                'twitter_url': 'https://twitter.com/example-joy',
                'website_url': 'https://example.com/joy',
                'order': 3,
            },
            {
                # Minimal organizer — all optional fields blank.
                'first_name': 'Liam',
                'last_name': 'Odhiambo',
                'community_role': 'Volunteer',
                'professional_role': '',
                'location': '',
                'github_url': '',
                'linkedin_url': '',
                'twitter_url': '',
                'website_url': '',
                'order': 4,
            },
        ]
        organizers = {}
        created = 0
        for spec in specs:
            org, was_created = Organizer.objects.get_or_create(
                first_name=spec['first_name'],
                last_name=spec['last_name'],
                defaults=spec,
            )
            organizers[f"{spec['first_name']} {spec['last_name']}"] = org
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(
            f'Organizers: {len(specs)} total ({created} new).'
        ))
        return organizers

    def _seed_partners(self, events):
        specs = [
            {
                'name': 'Demo Partner: Coastal Tech Hub',
                'description': 'A co-working space in Mombasa supporting local developer communities.',
                'website_url': 'https://example.com/coastal-tech-hub',
                'order': 1,
                'event_names': ['Demo: Async Django Workshop', 'Demo: Multi-day Coastal Conference'],
            },
            {
                'name': 'Demo Partner: PyKenya',
                'description': 'Python user group with chapters across Kenya.',
                'website_url': 'https://example.com/pykenya',
                'order': 2,
                'event_names': ['Demo: Async Django Workshop', 'Demo: External RSVP Meetup'],
            },
            {
                # Partner with no event associations — covers the empty-M2M case.
                'name': 'Demo Partner: Open Source Africa',
                'description': 'Pan-African open-source organisation we collaborate with.',
                'website_url': 'https://example.com/osa',
                'order': 3,
                'event_names': [],
            },
        ]
        created = 0
        for spec in specs:
            event_names = spec.pop('event_names')
            partner, was_created = Partner.objects.get_or_create(
                name=spec['name'],
                defaults=spec,
            )
            partner.events.set([events[n] for n in event_names if n in events])
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(
            f'Partners: {len(specs)} total ({created} new).'
        ))

    def _seed_sponsors(self, events):
        # One sponsor per Tier value, so the public site can render every tier.
        specs = [
            {
                'name': 'Demo Sponsor: ZanziPlatinum',
                'description': 'Top-tier sponsor backing flagship conferences.',
                'website_url': 'https://example.com/zanziplatinum',
                'tier': Sponsor.Tier.PLATINUM,
                'order': 1,
                'event_names': ['Demo: Multi-day Coastal Conference'],
            },
            {
                'name': 'Demo Sponsor: SwahiliCloud',
                'description': 'Regional cloud provider sponsoring community events.',
                'website_url': 'https://example.com/swahilicloud',
                'tier': Sponsor.Tier.GOLD,
                'order': 2,
                'event_names': ['Demo: Async Django Workshop', 'Demo: Multi-day Coastal Conference'],
            },
            {
                'name': 'Demo Sponsor: CoastSilver Labs',
                'description': 'Silver-tier sponsor supporting workshops.',
                'website_url': 'https://example.com/coastsilver',
                'tier': Sponsor.Tier.SILVER,
                'order': 3,
                'event_names': ['Demo: Async Django Workshop'],
            },
            {
                'name': 'Demo Sponsor: KenyaBronze Studios',
                'description': 'Bronze sponsor focused on grassroots meetups.',
                'website_url': 'https://example.com/kenyabronze',
                'tier': Sponsor.Tier.BRONZE,
                'order': 4,
                'event_names': ['Demo: Full Capacity Meetup'],
            },
            {
                'name': 'Demo Sponsor: Indian Ocean Devs',
                'description': 'Community sponsor for coastal developer events.',
                'website_url': 'https://example.com/iod',
                'tier': Sponsor.Tier.COMMUNITY,
                'order': 5,
                'event_names': ['Demo: External RSVP Meetup', 'Demo: Past Hack Night'],
            },
        ]
        created = 0
        for spec in specs:
            event_names = spec.pop('event_names')
            sponsor, was_created = Sponsor.objects.get_or_create(
                name=spec['name'],
                defaults=spec,
            )
            sponsor.events.set([events[n] for n in event_names if n in events])
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(
            f'Sponsors: {len(specs)} total ({created} new).'
        ))

    def _seed_social_links(self):
        specs = [
            {'name': 'Twitter', 'icon_class': 'bi bi-twitter-x', 'url': 'https://twitter.com/djangomombasa', 'order': 1},
            {'name': 'LinkedIn', 'icon_class': 'bi bi-linkedin', 'url': 'https://linkedin.com/company/djangomombasa', 'order': 2},
            {'name': 'GitHub', 'icon_class': 'bi bi-github', 'url': 'https://github.com/djangomombasa', 'order': 3},
            {'name': 'YouTube', 'icon_class': 'bi bi-youtube', 'url': 'https://youtube.com/@djangomombasa', 'order': 4},
            {'name': 'Telegram', 'icon_class': 'bi bi-telegram', 'url': 'https://t.me/djangomombasa', 'order': 5},
        ]
        created = 0
        for spec in specs:
            _, was_created = SocialLink.objects.get_or_create(
                name=spec['name'],
                defaults=spec,
            )
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(
            f'Social links: {len(specs)} total ({created} new).'
        ))

    def _seed_pages(self):
        specs = [
            {
                'slug': 'about',
                'title': 'About Django Mombasa',
                'content': '<p>Django Mombasa is a community for Python and Django developers on the Kenyan coast.</p>',
            },
            {
                'slug': 'code-of-conduct',
                'title': 'Code of Conduct',
                'content': '<p>We are committed to providing a welcoming and inclusive environment for everyone.</p>',
            },
            {
                'slug': 'faq',
                'title': 'Frequently Asked Questions',
                'content': (
                    '<h2>How do I join?</h2><p>Use the /membership/join/ form.</p>'
                    '<h2>How are events run?</h2><p>Most events happen on the Kenyan coast.</p>'
                ),
            },
            {
                'slug': 'sponsorship',
                'title': 'Sponsor Django Mombasa',
                'content': '<p>Reach out via the contact page if you want to support our events.</p>',
            },
        ]
        created = 0
        for spec in specs:
            _, was_created = Page.objects.get_or_create(
                slug=spec['slug'],
                defaults=spec,
            )
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(
            f'Pages: {len(specs)} total ({created} new).'
        ))

    def _seed_topics(self):
        names = ['Django', 'Python', 'Community', 'Career', 'Tooling', 'Testing']
        topics = {}
        for name in names:
            topic, _ = Topic.objects.get_or_create(name=name)
            topics[name] = topic
        self.stdout.write(self.style.SUCCESS(f'Topics: {", ".join(topics.keys())}'))
        return topics

    def _seed_articles(self, now, organizers, topics):
        author = organizers.get('Hellen Achieng')
        co_author = organizers.get('Ian Mutiso')
        specs = [
            {
                'title': 'Demo Article: Getting Started with Django on the Coast',
                'category': Article.Category.ARTICLE,
                'author': author,
                'summary': 'A beginner-friendly walkthrough for new Django developers in Mombasa.',
                'body': 'In this article we walk through setting up your first Django project...',
                'published_at': now - timezone.timedelta(days=3),
                'topic_names': ['Django', 'Community'],
            },
            {
                'title': 'Demo Guide: Deploying Django with Docker',
                'category': Article.Category.GUIDE,
                'author': author,
                'summary': 'A practical guide to containerising a Django app.',
                'body': 'This guide covers the Dockerfile, docker-compose, and production considerations...',
                'published_at': now - timezone.timedelta(days=10),
                'topic_names': ['Django', 'Python', 'Tooling'],
            },
            {
                # Draft — `published_at` is None, so it should NOT appear in the public list.
                'title': 'Demo Draft Article: Upcoming Django 7 Notes',
                'category': Article.Category.ARTICLE,
                'author': co_author,
                'summary': 'Unpublished draft for testing the published manager.',
                'body': 'Draft content that should not be visible on the public site...',
                'published_at': None,
                'topic_names': ['Django'],
            },
            {
                # Scheduled — `published_at` in the future, should NOT appear publicly.
                'title': 'Demo Scheduled Guide: Async Testing Patterns',
                'category': Article.Category.GUIDE,
                'author': co_author,
                'summary': 'Scheduled to publish next week — should not appear yet.',
                'body': 'Patterns for writing async tests in Django...',
                'published_at': now + timezone.timedelta(days=7),
                'topic_names': ['Testing', 'Django'],
            },
            {
                # Article with no author (FK set to NULL) — covers the SET_NULL path.
                'title': 'Demo Article: Anonymous Community Reflection',
                'category': Article.Category.ARTICLE,
                'author': None,
                'summary': 'Reflection submitted without an attributed author.',
                'body': 'A community member shares thoughts on a year of meetups...',
                'published_at': now - timezone.timedelta(days=30),
                'topic_names': ['Community', 'Career'],
            },
        ]
        created = 0
        for spec in specs:
            topic_names = spec.pop('topic_names')
            article, was_created = Article.objects.get_or_create(
                title=spec['title'],
                defaults=spec,
            )
            article.topics.set([topics[n] for n in topic_names])
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(
            f'Articles: {len(specs)} total ({created} new) — covers published/draft/scheduled and anonymous author.'
        ))

    def _seed_news_items(self, now, events, topics):
        past_event = events.get('Demo: Past Hack Night')
        conference = events.get('Demo: Multi-day Coastal Conference')
        specs = [
            {
                'title': 'Demo Newsletter: May Community Update',
                'kind': NewsItem.Kind.NEWSLETTER,
                'event': None,
                'issue_number': 1,
                'summary': 'A roundup of what happened in the community this month.',
                'body': 'This month we hosted a hack night and welcomed several new members...',
                'published_at': now - timezone.timedelta(days=2),
                'topic_names': ['Community'],
            },
            {
                'title': 'Demo Newsletter: April Community Update',
                'kind': NewsItem.Kind.NEWSLETTER,
                'event': None,
                'issue_number': 2,
                'summary': 'Last month at Django Mombasa.',
                'body': 'A look back at April activities, including our first workshop...',
                'published_at': now - timezone.timedelta(days=33),
                'topic_names': ['Community', 'Career'],
            },
            {
                'title': 'Demo Event Report: Past Hack Night',
                'kind': NewsItem.Kind.EVENT_REPORT,
                'event': past_event,
                'issue_number': None,
                'summary': 'Recap of our most recent hack night.',
                'body': 'Twenty members joined us for a night of pair programming and open-source contributions...',
                'published_at': now - timezone.timedelta(days=8),
                'topic_names': ['Community', 'Django'],
            },
            {
                # Draft newsletter — covers PublishedManager exclusion.
                'title': 'Demo Draft Newsletter: Coming Soon',
                'kind': NewsItem.Kind.NEWSLETTER,
                'event': None,
                'issue_number': 3,
                'summary': 'Draft preview of next month.',
                'body': 'Draft content — should not appear publicly yet...',
                'published_at': None,
                'topic_names': ['Community'],
            },
            {
                # Scheduled event report (tied to an upcoming conference) — should not appear yet.
                'title': 'Demo Scheduled Report: Coastal Conference Recap',
                'kind': NewsItem.Kind.EVENT_REPORT,
                'event': conference,
                'issue_number': None,
                'summary': 'Pre-written recap that publishes after the conference.',
                'body': 'Lots of great talks happened at the conference...',
                'published_at': now + timezone.timedelta(days=50),
                'topic_names': ['Community', 'Tooling'],
            },
        ]
        created = 0
        for spec in specs:
            topic_names = spec.pop('topic_names')
            item, was_created = NewsItem.objects.get_or_create(
                title=spec['title'],
                defaults=spec,
            )
            item.topics.set([topics[n] for n in topic_names])
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(
            f'News items: {len(specs)} total ({created} new) — covers newsletter/event-report, published/draft/scheduled.'
        ))
