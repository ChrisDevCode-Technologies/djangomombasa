from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from membership.models import Member

from .forms import RSVPForm
from .models import Event, RSVP


def _make_member(member_id='DM-001', email='alice@example.com', name='Alice'):
    m = Member(
        name=name,
        email=email,
        gender=Member.Gender.FEMALE,
        experience_level=Member.ExperienceLevel.MID,
        primary_language=Member.PrimaryLanguage.PYTHON,
    )
    m.save()
    if m.member_id != member_id:
        Member.objects.filter(pk=m.pk).update(member_id=member_id)
        m.refresh_from_db()
    return m


def _make_event(has_rsvp=True, name='Test Meetup'):
    return Event.objects.create(
        name=name,
        date=timezone.now() + timezone.timedelta(days=7),
        details='A test event.',
        has_rsvp=has_rsvp,
    )


class RSVPFormLookupTests(TestCase):
    def test_resolves_by_member_id_case_insensitive(self):
        m = _make_member(member_id='DM-042', email='caseins@example.com')
        form = RSVPForm(data={'member_identifier': 'dm-042'})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_member.pk, m.pk)

    def test_resolves_by_email_exact(self):
        m = _make_member(member_id='DM-043', email='bob@example.com')
        form = RSVPForm(data={'member_identifier': 'bob@example.com'})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_member.pk, m.pk)

    def test_rejects_unknown_identifier(self):
        form = RSVPForm(data={'member_identifier': 'DM-999'})
        self.assertFalse(form.is_valid())
        self.assertIn('member_identifier', form.errors)


class RSVPViewTests(TestCase):
    def test_404_when_flag_off(self):
        event = _make_event(has_rsvp=False, name='Closed Event')
        resp = self.client.get(reverse('events_and_activities:event_rsvp', args=[event.slug]))
        self.assertEqual(resp.status_code, 404)

    def test_successful_rsvp_creates_row_and_redirects(self):
        event = _make_event(has_rsvp=True, name='Open Event')
        member = _make_member(member_id='DM-100', email='c@example.com')
        resp = self.client.post(
            reverse('events_and_activities:event_rsvp', args=[event.slug]),
            {'member_identifier': 'DM-100'},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(RSVP.objects.filter(event=event, member=member).exists())

    def test_duplicate_rsvp_rejected_with_form_error(self):
        event = _make_event(has_rsvp=True, name='Dupe Event')
        member = _make_member(member_id='DM-200', email='d@example.com')
        RSVP.objects.create(event=event, member=member)
        resp = self.client.post(
            reverse('events_and_activities:event_rsvp', args=[event.slug]),
            {'member_identifier': 'DM-200'},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'has already RSVPed')
        self.assertEqual(RSVP.objects.filter(event=event, member=member).count(), 1)


class CFPViewTests(TestCase):
    def test_404_when_flag_off(self):
        event = Event.objects.create(
            name='No CFP', date=timezone.now() + timezone.timedelta(days=7),
            details='x', has_cfp=False,
        )
        resp = self.client.get(reverse('events_and_activities:event_cfs', args=[event.slug]))
        self.assertEqual(resp.status_code, 404)

    def test_get_renders_form(self):
        event = Event.objects.create(
            name='CFP Open', date=timezone.now() + timezone.timedelta(days=7),
            details='x', has_cfp=True,
        )
        resp = self.client.get(reverse('events_and_activities:event_cfs', args=[event.slug]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Submit proposal')

    def test_post_creates_proposal_and_redirects(self):
        from .models import SpeakerProposal
        event = Event.objects.create(
            name='CFP Sub', date=timezone.now() + timezone.timedelta(days=7),
            details='x', has_cfp=True,
        )
        resp = self.client.post(
            reverse('events_and_activities:event_cfs', args=[event.slug]),
            {
                'name': 'Jane Speaker',
                'email': 'jane@example.com',
                'proposed_talk_title': 'Async Django',
                'talk_abstract': 'A talk about async views.',
                'bio': '',
            },
        )
        self.assertEqual(resp.status_code, 302)
        proposal = SpeakerProposal.objects.get(event=event)
        self.assertEqual(proposal.status, SpeakerProposal.Status.PENDING)
        self.assertEqual(proposal.name, 'Jane Speaker')


class CFVViewTests(TestCase):
    def test_404_when_flag_off(self):
        event = Event.objects.create(
            name='No CFV', date=timezone.now() + timezone.timedelta(days=7),
            details='x', has_cfv=False,
        )
        resp = self.client.get(reverse('events_and_activities:event_cfv', args=[event.slug]))
        self.assertEqual(resp.status_code, 404)

    def test_get_renders_form(self):
        event = Event.objects.create(
            name='CFV Open', date=timezone.now() + timezone.timedelta(days=7),
            details='x', has_cfv=True,
        )
        resp = self.client.get(reverse('events_and_activities:event_cfv', args=[event.slug]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Sign up to volunteer')

    def test_post_creates_signup_and_redirects(self):
        from .models import VolunteerSignup
        event = Event.objects.create(
            name='CFV Sub', date=timezone.now() + timezone.timedelta(days=7),
            details='x', has_cfv=True,
        )
        resp = self.client.post(
            reverse('events_and_activities:event_cfv', args=[event.slug]),
            {
                'name': 'Joe Helper',
                'email': 'joe@example.com',
                'phone': '',
                'availability': 'Mornings',
                'skills_or_role': 'Registration desk',
            },
        )
        self.assertEqual(resp.status_code, 302)
        signup = VolunteerSignup.objects.get(event=event)
        self.assertEqual(signup.status, VolunteerSignup.Status.PENDING)
        self.assertEqual(signup.skills_or_role, 'Registration desk')


class EventDetailFlagButtonsTests(TestCase):
    def test_all_three_buttons_render_when_flags_on(self):
        event = Event.objects.create(
            name='All On', date=timezone.now() + timezone.timedelta(days=7),
            details='x', has_rsvp=True, has_cfp=True, has_cfv=True,
        )
        resp = self.client.get(reverse('events_and_activities:event_detail', args=[event.slug]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'RSVP for This Event')
        self.assertContains(resp, 'Call for Speakers')
        self.assertContains(resp, 'Call for Volunteers')

    def test_external_link_fallback_when_has_rsvp_false(self):
        event = Event.objects.create(
            name='Fallback', date=timezone.now() + timezone.timedelta(days=7),
            details='x', has_rsvp=False, rsvp_link='https://example.com/rsvp',
        )
        resp = self.client.get(reverse('events_and_activities:event_detail', args=[event.slug]))
        self.assertContains(resp, 'https://example.com/rsvp')
        self.assertNotContains(resp, reverse('events_and_activities:event_rsvp', args=[event.slug]))
