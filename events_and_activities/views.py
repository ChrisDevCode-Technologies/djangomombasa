from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from app import emails as notifications

from .forms import RSVPForm, RSVPGuestForm, SpeakerProposalForm, VolunteerSignupForm
from .models import Event, RSVP


def events(request):
    upcoming = Event.objects.filter(date__gte=timezone.now())
    past = Event.objects.filter(date__lt=timezone.now()).order_by('-date')
    return render(request, 'events_and_activities/events.html', {'upcoming': upcoming, 'past': past})


def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug)
    return render(request, 'events_and_activities/event_detail.html', {'event': event})


def _get_event_with_flag(slug, flag):
    event = get_object_or_404(Event, slug=slug)
    if not getattr(event, flag):
        raise Http404('This feature is not enabled for this event.')
    return event


@require_http_methods(['GET', 'POST'])
def rsvp(request, slug):
    event = _get_event_with_flag(slug, 'has_rsvp')
    member_form = RSVPForm()
    guest_form = RSVPGuestForm()
    active_tab = 'member'
    if request.method == 'POST':
        mode = request.POST.get('mode', 'member')
        if mode == 'guest':
            active_tab = 'guest'
            guest_form = RSVPGuestForm(request.POST)
            if guest_form.is_valid():
                guest = guest_form.resolve_or_create_guest()
                if RSVP.objects.filter(event=event, member=guest).exists():
                    guest_form.add_error('email', 'This email has already RSVPed to this event.')
                else:
                    rsvp_obj = RSVP.objects.create(event=event, member=guest)
                    notifications.send_rsvp_confirmation(rsvp_obj)
                    return redirect('events_and_activities:event_rsvp_success', slug=event.slug, rsvp_id=rsvp_obj.pk)
        else:
            member_form = RSVPForm(request.POST)
            if member_form.is_valid():
                member = member_form.cleaned_member
                if RSVP.objects.filter(event=event, member=member).exists():
                    member_form.add_error('member_identifier', f'{member.member_id} has already RSVPed to this event.')
                else:
                    rsvp_obj = RSVP.objects.create(event=event, member=member)
                    notifications.send_rsvp_confirmation(rsvp_obj)
                    return redirect('events_and_activities:event_rsvp_success', slug=event.slug, rsvp_id=rsvp_obj.pk)
    return render(request, 'events_and_activities/rsvp.html', {
        'event': event,
        'member_form': member_form,
        'guest_form': guest_form,
        'active_tab': active_tab,
    })


def rsvp_success(request, slug, rsvp_id):
    event = get_object_or_404(Event, slug=slug)
    rsvp_obj = get_object_or_404(RSVP, pk=rsvp_id, event=event)
    return render(request, 'events_and_activities/rsvp_success.html', {'event': event, 'rsvp': rsvp_obj})


@require_http_methods(['GET', 'POST'])
def call_for_speakers(request, slug):
    event = _get_event_with_flag(slug, 'has_cfp')
    if request.method == 'POST':
        form = SpeakerProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.event = event
            proposal.save()
            notifications.send_speaker_proposal_received(proposal)
            return redirect('events_and_activities:event_cfs_thanks', slug=event.slug)
    else:
        form = SpeakerProposalForm()
    return render(request, 'events_and_activities/call_for_speakers.html', {'event': event, 'form': form})


def cfp_thank_you(request, slug):
    event = get_object_or_404(Event, slug=slug)
    return render(request, 'events_and_activities/call_for_speakers_thanks.html', {'event': event})


@require_http_methods(['GET', 'POST'])
def call_for_volunteers(request, slug):
    event = _get_event_with_flag(slug, 'has_cfv')
    if request.method == 'POST':
        form = VolunteerSignupForm(request.POST)
        if form.is_valid():
            signup = form.save(commit=False)
            signup.event = event
            signup.save()
            notifications.send_volunteer_signup_received(signup)
            return redirect('events_and_activities:event_cfv_thanks', slug=event.slug)
    else:
        form = VolunteerSignupForm()
    return render(request, 'events_and_activities/call_for_volunteers.html', {'event': event, 'form': form})


def cfv_thank_you(request, slug):
    event = get_object_or_404(Event, slug=slug)
    return render(request, 'events_and_activities/call_for_volunteers_thanks.html', {'event': event})
