from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from membership.models import Member, RSVPGuest

from .forms import RSVPForm, RSVPGuestForm
from .models import Event, RSVP, ScheduleSlot, SpeakerProposal


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


class RSVPGuestFlowTests(TestCase):
    def test_guest_rsvp_creates_guest_and_rsvp(self):
        event = _make_event(has_rsvp=True, name='Guest Welcome')
        resp = self.client.post(
            reverse('events_and_activities:event_rsvp', args=[event.slug]),
            {
                'mode': 'guest',
                'name': 'Grace Guest',
                'email': 'grace@example.com',
                'receive_email_communications': 'on',
            },
        )
        self.assertEqual(resp.status_code, 302)
        guest = RSVPGuest.objects.get(email='grace@example.com')
        self.assertEqual(guest.name, 'Grace Guest')
        self.assertEqual(guest.kind, Member.Kind.RSVP_GUEST)
        self.assertTrue(guest.receive_email_communications)
        self.assertTrue(RSVP.objects.filter(event=event, member=guest).exists())

    def test_guest_rsvp_reuses_existing_member_email(self):
        event = _make_event(has_rsvp=True, name='Reuse Event')
        existing = _make_member(member_id='DM-300', email='existing@example.com')
        resp = self.client.post(
            reverse('events_and_activities:event_rsvp', args=[event.slug]),
            {
                'mode': 'guest',
                'name': 'Ignored Name',
                'email': 'existing@example.com',
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Member.objects.filter(email='existing@example.com').count(), 1)
        rsvp_obj = RSVP.objects.get(event=event)
        self.assertEqual(rsvp_obj.member.pk, existing.pk)

    def test_guest_rsvp_reuses_existing_guest_email(self):
        event_a = _make_event(has_rsvp=True, name='Event A')
        event_b = _make_event(has_rsvp=True, name='Event B')
        self.client.post(
            reverse('events_and_activities:event_rsvp', args=[event_a.slug]),
            {'mode': 'guest', 'name': 'Repeat Guest', 'email': 'repeat@example.com'},
        )
        self.client.post(
            reverse('events_and_activities:event_rsvp', args=[event_b.slug]),
            {'mode': 'guest', 'name': 'Repeat Guest', 'email': 'repeat@example.com'},
        )
        self.assertEqual(Member.objects.filter(email='repeat@example.com').count(), 1)
        guest = RSVPGuest.objects.get(email='repeat@example.com')
        self.assertEqual(RSVP.objects.filter(member=guest).count(), 2)

    def test_guest_duplicate_rsvp_rejected(self):
        event = _make_event(has_rsvp=True, name='Dup Guest Event')
        self.client.post(
            reverse('events_and_activities:event_rsvp', args=[event.slug]),
            {'mode': 'guest', 'name': 'Dup Guest', 'email': 'dup@example.com'},
        )
        resp = self.client.post(
            reverse('events_and_activities:event_rsvp', args=[event.slug]),
            {'mode': 'guest', 'name': 'Dup Guest', 'email': 'dup@example.com'},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'has already RSVPed')
        self.assertEqual(RSVP.objects.filter(event=event).count(), 1)

    def test_guest_form_requires_name_and_email(self):
        form = RSVPGuestForm(data={'name': '', 'email': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('email', form.errors)

    def test_member_form_ignores_rsvp_guest_email(self):
        # A guest's email should NOT be resolvable through the members-only RSVPForm.
        guest = RSVPGuest(name='Lone Guest', email='lone@example.com')
        guest.save()
        form = RSVPForm(data={'member_identifier': 'lone@example.com'})
        self.assertFalse(form.is_valid())
        self.assertIn('member_identifier', form.errors)

    def test_rsvp_view_renders_both_forms(self):
        event = _make_event(has_rsvp=True, name='Two Form Event')
        resp = self.client.get(reverse('events_and_activities:event_rsvp', args=[event.slug]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'I\'m a member')
        self.assertContains(resp, 'RSVP as a guest')
        self.assertContains(resp, 'name="mode" value="member"')
        self.assertContains(resp, 'name="mode" value="guest"')


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


class RSVPCapacityAndDeadlineTests(TestCase):
    def test_rsvp_is_open_when_no_limits(self):
        event = _make_event(has_rsvp=True, name='Open No Limits')
        self.assertTrue(event.rsvp_is_open)
        self.assertIsNone(event.rsvp_closed_reason)

    def test_rsvp_is_full_when_capacity_reached(self):
        event = Event.objects.create(
            name='Tiny', date=timezone.now() + timezone.timedelta(days=7),
            details='x', has_rsvp=True, rsvp_capacity=1,
        )
        m = _make_member(member_id='DM-500', email='one@example.com')
        RSVP.objects.create(event=event, member=m)
        self.assertTrue(event.rsvp_is_full)
        self.assertFalse(event.rsvp_is_open)
        self.assertEqual(event.rsvp_closed_reason, 'full')

    def test_rsvp_closed_when_deadline_passed(self):
        event = Event.objects.create(
            name='Past', date=timezone.now() + timezone.timedelta(days=7),
            details='x', has_rsvp=True,
            rsvp_deadline=timezone.now() - timezone.timedelta(hours=1),
        )
        self.assertTrue(event.rsvp_deadline_passed)
        self.assertFalse(event.rsvp_is_open)
        self.assertEqual(event.rsvp_closed_reason, 'past_deadline')

    def test_rsvp_view_shows_closed_state_when_full(self):
        event = Event.objects.create(
            name='Full Event', date=timezone.now() + timezone.timedelta(days=7),
            details='x', has_rsvp=True, rsvp_capacity=1,
        )
        m = _make_member(member_id='DM-510', email='occupant@example.com')
        RSVP.objects.create(event=event, member=m)
        resp = self.client.get(reverse('events_and_activities:event_rsvp', args=[event.slug]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'event is full')
        self.assertNotContains(resp, 'Confirm RSVP')

    def test_rsvp_post_rejected_when_full(self):
        event = Event.objects.create(
            name='No Room', date=timezone.now() + timezone.timedelta(days=7),
            details='x', has_rsvp=True, rsvp_capacity=1,
        )
        occupant = _make_member(member_id='DM-520', email='taken@example.com')
        RSVP.objects.create(event=event, member=occupant)
        latecomer = _make_member(member_id='DM-521', email='late@example.com')
        resp = self.client.post(
            reverse('events_and_activities:event_rsvp', args=[event.slug]),
            {'mode': 'member', 'member_identifier': 'DM-521'},
        )
        self.assertEqual(resp.status_code, 200)
        # Closed-state banner is rendered; no new RSVP was created.
        self.assertFalse(RSVP.objects.filter(event=event, member=latecomer).exists())


class RSVPCheckInTests(TestCase):
    def test_token_is_unique(self):
        event = _make_event(has_rsvp=True, name='Token Event')
        m1 = _make_member(member_id='DM-600', email='a@example.com')
        m2 = _make_member(member_id='DM-601', email='b@example.com')
        r1 = RSVP.objects.create(event=event, member=m1)
        r2 = RSVP.objects.create(event=event, member=m2)
        self.assertIsNotNone(r1.check_in_token)
        self.assertIsNotNone(r2.check_in_token)
        self.assertNotEqual(r1.check_in_token, r2.check_in_token)

    def test_default_check_in_status_is_pending(self):
        event = _make_event(has_rsvp=True, name='Pending Event')
        m = _make_member(member_id='DM-610', email='c@example.com')
        r = RSVP.objects.create(event=event, member=m)
        self.assertEqual(r.check_in_status, RSVP.CheckInStatus.PENDING)
        self.assertIsNone(r.checked_in_at)


class ScheduleSlotTests(TestCase):
    def test_clean_rejects_both_speaker_sources(self):
        event = _make_event(has_rsvp=False, name='Schedule Event')
        proposal = SpeakerProposal.objects.create(
            event=event, name='Approved Speaker', email='spk@example.com',
            proposed_talk_title='Talk', talk_abstract='abstract',
            status=SpeakerProposal.Status.APPROVED,
        )
        slot = ScheduleSlot(
            event=event,
            title='Conflict',
            speaker_proposal=proposal,
            manual_speaker_name='Someone Else',
        )
        with self.assertRaises(ValidationError):
            slot.clean()

    def test_speaker_display_name_prefers_proposal(self):
        event = _make_event(has_rsvp=False, name='Display Event')
        proposal = SpeakerProposal.objects.create(
            event=event, name='Dr. Approved', email='dr@example.com',
            proposed_talk_title='Title', talk_abstract='Abstract',
            status=SpeakerProposal.Status.APPROVED,
        )
        slot = ScheduleSlot.objects.create(event=event, title='Keynote', speaker_proposal=proposal)
        self.assertEqual(slot.speaker_display_name, 'Dr. Approved')

    def test_speaker_display_name_falls_back_to_manual(self):
        event = _make_event(has_rsvp=False, name='Manual Event')
        slot = ScheduleSlot.objects.create(
            event=event, title='Coffee + Manual',
            manual_speaker_name='Jamie External',
            manual_speaker_bio='Friend of the group.',
        )
        self.assertEqual(slot.speaker_display_name, 'Jamie External')
        self.assertEqual(slot.speaker_display_bio, 'Friend of the group.')

    def test_event_detail_renders_schedule_section(self):
        event = _make_event(has_rsvp=False, name='With Programme')
        ScheduleSlot.objects.create(event=event, title='Welcome remarks', order=1, manual_speaker_name='Host')
        resp = self.client.get(reverse('events_and_activities:event_detail', args=[event.slug]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Schedule')
        self.assertContains(resp, 'Welcome remarks')
        self.assertContains(resp, 'Host')
