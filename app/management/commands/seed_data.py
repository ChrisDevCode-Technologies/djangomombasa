from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models import Organizer, Page, Partner, SocialLink, Sponsor
from blog_and_news.models import Article, NewsItem, Topic
from events_and_activities.models import (
    Event,
    RSVP,
    SpeakerProposal,
    Tag,
    VolunteerSignup,
)
from membership.models import Member


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


DEMO_EVENT_NAMES = [
    'Demo: Async Django Workshop',
    'Demo: External RSVP Meetup',
    'Demo: Past Hack Night',
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
        tags = self._seed_tags()
        events = self._seed_events(now, tags)
        self._seed_submissions(events, members)
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
        email = 'member@mail.com'
        _, was_created = User.objects.get_or_create(
            email=email,
            defaults={'is_staff': False, 'is_superuser': False},
        )
        verb = 'Created' if was_created else 'Exists'
        self.stdout.write(self.style.SUCCESS(f'User: {verb} {email}'))

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
                'event_names': ['Demo: Async Django Workshop'],
            },
            {
                'name': 'Demo Partner: PyKenya',
                'description': 'Python user group with chapters across Kenya.',
                'website_url': 'https://example.com/pykenya',
                'order': 2,
                'event_names': ['Demo: Async Django Workshop', 'Demo: External RSVP Meetup'],
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
        specs = [
            {
                'name': 'Demo Sponsor: SwahiliCloud',
                'description': 'Regional cloud provider sponsoring community events.',
                'website_url': 'https://example.com/swahilicloud',
                'tier': Sponsor.Tier.GOLD,
                'order': 1,
                'event_names': ['Demo: Async Django Workshop'],
            },
            {
                'name': 'Demo Sponsor: Indian Ocean Devs',
                'description': 'Community sponsor for coastal developer events.',
                'website_url': 'https://example.com/iod',
                'tier': Sponsor.Tier.COMMUNITY,
                'order': 2,
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
        names = ['Django', 'Python', 'Community', 'Career']
        topics = {}
        for name in names:
            topic, _ = Topic.objects.get_or_create(name=name)
            topics[name] = topic
        self.stdout.write(self.style.SUCCESS(f'Topics: {", ".join(topics.keys())}'))
        return topics

    def _seed_articles(self, now, organizers, topics):
        author = organizers.get('Hellen Achieng')
        specs = [
            {
                'title': 'Demo Article: Getting Started with Django on the Coast',
                'category': Article.Category.ARTICLE,
                'summary': 'A beginner-friendly walkthrough for new Django developers in Mombasa.',
                'body': 'In this article we walk through setting up your first Django project...',
                'published_at': now - timezone.timedelta(days=3),
                'topic_names': ['Django', 'Community'],
            },
            {
                'title': 'Demo Guide: Deploying Django with Docker',
                'category': Article.Category.GUIDE,
                'summary': 'A practical guide to containerising a Django app.',
                'body': 'This guide covers the Dockerfile, docker-compose, and production considerations...',
                'published_at': now - timezone.timedelta(days=10),
                'topic_names': ['Django', 'Python'],
            },
        ]
        created = 0
        for spec in specs:
            topic_names = spec.pop('topic_names')
            article, was_created = Article.objects.get_or_create(
                title=spec['title'],
                defaults={**spec, 'author': author},
            )
            article.topics.set([topics[n] for n in topic_names])
            created += int(was_created)
        self.stdout.write(self.style.SUCCESS(
            f'Articles: {len(specs)} total ({created} new).'
        ))

    def _seed_news_items(self, now, events, topics):
        past_event = events.get('Demo: Past Hack Night')
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
                'title': 'Demo Event Report: Past Hack Night',
                'kind': NewsItem.Kind.EVENT_REPORT,
                'event': past_event,
                'issue_number': None,
                'summary': 'Recap of our most recent hack night.',
                'body': 'Twenty members joined us for a night of pair programming and open-source contributions...',
                'published_at': now - timezone.timedelta(days=8),
                'topic_names': ['Community', 'Django'],
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
            f'News items: {len(specs)} total ({created} new).'
        ))
