from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Count, Max, Q
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from events_and_activities.models import Event, RSVP, ScheduleSlot, SpeakerProposal, VolunteerSignup
from membership.models import Member

from . import emails as notifications
from .forms import BroadcastForm, EventForm, MemberAdminForm, ScheduleSlotForm


def staff_required(view):
    @wraps(view)
    @login_required(login_url='custom_admin:admin_login')
    @user_passes_test(lambda u: u.is_staff, login_url='custom_admin:admin_login')
    def _wrapped(request, *args, **kwargs):
        return view(request, *args, **kwargs)
    return _wrapped


def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('custom_admin:dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                next_url = request.GET.get('next') or reverse('custom_admin:dashboard')
                return redirect(next_url)
            form.add_error(None, 'This account does not have staff access.')
    else:
        form = AuthenticationForm(request)

    return render(request, 'custom_admin/login.html', {'form': form})


def admin_logout(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    logout(request)
    return redirect('custom_admin:admin_login')


@staff_required
def dashboard(request):
    now = timezone.now()
    context = {
        'event_count': Event.objects.count(),
        'upcoming_event_count': Event.objects.filter(date__gte=now).count(),
        'member_count': Member.objects.filter(kind=Member.Kind.MEMBER).count(),
        'guest_count': Member.objects.filter(kind=Member.Kind.RSVP_GUEST).count(),
    }
    return render(request, 'custom_admin/dashboard.html', context)


@staff_required
def event_list(request):
    now = timezone.now()
    upcoming = Event.objects.filter(date__gte=now).order_by('date').prefetch_related('tags')
    past = Event.objects.filter(date__lt=now).order_by('-date').prefetch_related('tags')
    return render(request, 'custom_admin/events/list.html', {
        'upcoming_events': upcoming,
        'past_events': past,
    })


@staff_required
def event_detail(request, slug):
    event = get_object_or_404(
        Event.objects.prefetch_related(
            'tags',
            'rsvps__member',
            'speaker_proposals',
            'volunteer_signups',
            'schedule_slots__speaker_proposal',
        ),
        slug=slug,
    )
    return render(request, 'custom_admin/events/detail.html', {
        'event': event,
        'rsvp_count': event.rsvps.count(),
        'speaker_proposal_count': event.speaker_proposals.count(),
        'volunteer_signup_count': event.volunteer_signups.count(),
        'schedule_slot_count': event.schedule_slots.count(),
    })


@staff_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            messages.success(request, f'Event "{event.name}" created.')
            return redirect('custom_admin:event_detail', slug=event.slug)
    else:
        form = EventForm()
    return render(request, 'custom_admin/events/form.html', {
        'form': form,
        'mode': 'create',
        'page_title': 'New Event',
    })


@staff_required
def event_edit(request, slug):
    event = get_object_or_404(Event, slug=slug)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save()
            messages.success(request, f'Event "{event.name}" updated.')
            return redirect('custom_admin:event_detail', slug=event.slug)
    else:
        form = EventForm(instance=event)
    return render(request, 'custom_admin/events/form.html', {
        'form': form,
        'event': event,
        'mode': 'edit',
        'page_title': f'Edit: {event.name}',
    })


@staff_required
def member_list(request):
    q = request.GET.get('q', '').strip()
    members = Member.objects.annotate(
        rsvp_count=Count('event_rsvps', distinct=True),
        attended_count=Count(
            'event_rsvps',
            filter=Q(event_rsvps__check_in_status=RSVP.CheckInStatus.ACCEPTED),
            distinct=True,
        ),
    ).order_by('-joined_at')
    if q:
        members = members.filter(
            Q(name__icontains=q)
            | Q(email__icontains=q)
            | Q(member_id__icontains=q)
        )
    return render(request, 'custom_admin/members/list.html', {
        'members': members,
        'q': q,
    })


@staff_required
def member_detail(request, member_id):
    member = get_object_or_404(Member, member_id=member_id)
    rsvps = member.event_rsvps.select_related('event').order_by('-event__date')
    attended = rsvps.filter(check_in_status=RSVP.CheckInStatus.ACCEPTED)
    return render(request, 'custom_admin/members/detail.html', {
        'member': member,
        'rsvps': rsvps,
        'attended_rsvps': attended,
        'rsvp_count': rsvps.count(),
        'attended_count': attended.count(),
    })


@staff_required
def member_create(request):
    if request.method == 'POST':
        form = MemberAdminForm(request.POST)
        if form.is_valid():
            member = form.save()
            messages.success(request, f'Member {member.member_id} ({member.name}) created.')
            return redirect('custom_admin:member_detail', member_id=member.member_id)
    else:
        form = MemberAdminForm()
    return render(request, 'custom_admin/members/form.html', {
        'form': form,
        'mode': 'create',
        'page_title': 'New Member',
    })


@staff_required
def member_edit(request, member_id):
    member = get_object_or_404(Member, member_id=member_id)
    if request.method == 'POST':
        form = MemberAdminForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, f'Member {member.member_id} updated.')
            return redirect('custom_admin:member_detail', member_id=member.member_id)
    else:
        form = MemberAdminForm(instance=member)
    return render(request, 'custom_admin/members/form.html', {
        'form': form,
        'member': member,
        'mode': 'edit',
        'page_title': f'Edit: {member.name}',
    })


def _update_status(request, instance, allowed_statuses, label, notify=None):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    new_status = request.POST.get('status', '').strip()
    if new_status not in allowed_statuses:
        messages.error(request, f'Invalid status "{new_status}".')
    else:
        previous_status = instance.status
        if previous_status == new_status:
            messages.info(request, f'{label} #{instance.pk} is already {instance.get_status_display()}.')
        else:
            instance.status = new_status
            instance.save(update_fields=['status'])
            sent = bool(notify and notify(instance, previous_status))
            if sent:
                messages.success(
                    request,
                    f'{label} #{instance.pk} marked {instance.get_status_display()} — email sent to {instance.email}.',
                )
            else:
                messages.success(
                    request,
                    f'{label} #{instance.pk} marked {instance.get_status_display()}.',
                )
                if notify is not None:
                    messages.warning(request, f'Status email to {instance.email} failed to send — check the mail server logs.')
    return redirect('custom_admin:event_detail', slug=instance.event.slug)


def _audience_recipients(audience: str, event=None):
    """Resolve an audience choice + optional event into (label, list_of_email_strings)."""
    if audience == 'members':
        qs = Member.objects.filter(kind=Member.Kind.MEMBER).exclude(email='')
        return 'All community members', list(qs.values_list('email', flat=True))
    if audience == 'members_subscribed':
        qs = (
            Member.objects.filter(kind=Member.Kind.MEMBER, receive_email_communications=True)
            .exclude(email='')
        )
        return 'Members opted in to email', list(qs.values_list('email', flat=True))
    if audience == 'rsvps' and event is not None:
        qs = event.rsvps.select_related('member').exclude(member__email='')
        return f'RSVPs for {event.name}', [r.member.email for r in qs]
    if audience == 'speakers' and event is not None:
        qs = event.speaker_proposals.exclude(email='')
        return f'Speaker proposers for {event.name}', list(qs.values_list('email', flat=True))
    if audience == 'speakers_approved' and event is not None:
        qs = event.speaker_proposals.filter(status=SpeakerProposal.Status.APPROVED).exclude(email='')
        return f'Approved speakers for {event.name}', list(qs.values_list('email', flat=True))
    if audience == 'volunteers' and event is not None:
        qs = event.volunteer_signups.exclude(email='')
        return f'Volunteers for {event.name}', list(qs.values_list('email', flat=True))
    if audience == 'volunteers_approved' and event is not None:
        qs = event.volunteer_signups.filter(status=VolunteerSignup.Status.APPROVED).exclude(email='')
        return f'Approved volunteers for {event.name}', list(qs.values_list('email', flat=True))
    return 'Unknown audience', []


@staff_required
def broadcast(request):
    preview = None
    if request.method == 'POST':
        form = BroadcastForm(request.POST)
        if form.is_valid():
            audience = form.cleaned_data['audience']
            event = form.cleaned_data.get('event')
            label, emails = _audience_recipients(audience, event)
            if request.POST.get('action') == 'preview':
                preview = {'label': label, 'emails': emails, 'count': len(emails)}
            else:
                if not emails:
                    messages.warning(request, f'No recipients found for: {label}.')
                else:
                    sent = notifications.send_broadcast(
                        subject=form.cleaned_data['subject'],
                        body=form.cleaned_data['body'],
                        recipients=emails,
                        event=event,
                        context_label=label,
                    )
                    if sent:
                        messages.success(request, f'Sent {sent} email(s) to: {label}.')
                    else:
                        messages.error(request, 'No emails were sent. Check the mail server logs.')
                    return redirect('custom_admin:broadcast')
    else:
        form = BroadcastForm(initial={'event': request.GET.get('event') or None})
    return render(request, 'custom_admin/messaging/broadcast.html', {
        'form': form,
        'preview': preview,
    })


@staff_required
def speaker_proposal_status(request, pk):
    proposal = get_object_or_404(SpeakerProposal.objects.select_related('event'), pk=pk)
    return _update_status(
        request,
        proposal,
        {s.value for s in SpeakerProposal.Status},
        label='Speaker proposal',
        notify=notifications.send_speaker_proposal_status_changed,
    )


@staff_required
def volunteer_signup_status(request, pk):
    signup = get_object_or_404(VolunteerSignup.objects.select_related('event'), pk=pk)
    return _update_status(
        request,
        signup,
        {s.value for s in VolunteerSignup.Status},
        label='Volunteer signup',
        notify=notifications.send_volunteer_signup_status_changed,
    )


# --- RSVP check-in -----------------------------------------------------------

@staff_required
def check_in_picker(request):
    now = timezone.now()
    events = (
        Event.objects.filter(has_rsvp=True)
        .annotate(
            rsvp_total=Count('rsvps', distinct=True),
            accepted_total=Count(
                'rsvps',
                filter=Q(rsvps__check_in_status=RSVP.CheckInStatus.ACCEPTED),
                distinct=True,
            ),
        )
        .order_by('date')
    )
    upcoming = [e for e in events if e.date >= now - timezone.timedelta(hours=12)]
    past = [e for e in events if e.date < now - timezone.timedelta(hours=12)][::-1]
    return render(request, 'custom_admin/events/check_in_picker.html', {
        'upcoming_events': upcoming,
        'past_events': past,
    })


@staff_required
def event_check_in(request, slug):
    event = get_object_or_404(Event, slug=slug)
    q = request.GET.get('q', '').strip()
    token = request.GET.get('token', '').strip()

    rsvps = event.rsvps.select_related('member').order_by('member__name')
    highlighted_pk = None

    if token:
        match = rsvps.filter(check_in_token=token).first() if _looks_like_uuid(token) else None
        if match:
            highlighted_pk = match.pk
        else:
            messages.warning(request, 'No RSVP matched that QR code for this event.')

    if q:
        rsvps = rsvps.filter(
            Q(member__email__icontains=q)
            | Q(member__name__icontains=q)
            | Q(member__member_id__icontains=q)
        )

    return render(request, 'custom_admin/events/check_in.html', {
        'event': event,
        'rsvps': rsvps,
        'q': q,
        'token': token,
        'highlighted_pk': highlighted_pk,
        'rsvp_count': event.rsvps.count(),
        'accepted_count': event.rsvps.filter(check_in_status=RSVP.CheckInStatus.ACCEPTED).count(),
        'status_choices': RSVP.CheckInStatus.choices,
        'check_in_is_open': event.check_in_is_open,
        'check_in_opens_at': event.check_in_opens_at,
    })


def _looks_like_uuid(value: str) -> bool:
    try:
        import uuid as _uuid
        _uuid.UUID(value)
        return True
    except (ValueError, AttributeError):
        return False


@staff_required
def rsvp_check_in_status(request, pk):
    rsvp = get_object_or_404(RSVP.objects.select_related('event', 'member'), pk=pk)
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    new_status = request.POST.get('status', '').strip()
    allowed = {s.value for s in RSVP.CheckInStatus}
    if new_status not in allowed:
        messages.error(request, f'Invalid status "{new_status}".')
        return redirect('custom_admin:event_check_in', slug=rsvp.event.slug)

    if not rsvp.event.check_in_is_open:
        opens_at = timezone.localtime(rsvp.event.check_in_opens_at)
        messages.error(
            request,
            f'Check-in opens at {opens_at:%H:%M on %d %b} (2 hours before the event).',
        )
        return redirect('custom_admin:event_check_in', slug=rsvp.event.slug)

    previous_status = rsvp.check_in_status
    if previous_status == new_status:
        messages.info(request, f'{rsvp.member.name} is already {rsvp.get_check_in_status_display()}.')
        return redirect('custom_admin:event_check_in', slug=rsvp.event.slug)

    rsvp.check_in_status = new_status
    update_fields = ['check_in_status']
    if new_status == RSVP.CheckInStatus.ACCEPTED and rsvp.checked_in_at is None:
        rsvp.checked_in_at = timezone.now()
        update_fields.append('checked_in_at')
    rsvp.save(update_fields=update_fields)

    sent = bool(notifications.send_rsvp_check_in_status_changed(rsvp, previous_status))
    if sent:
        messages.success(
            request,
            f'{rsvp.member.name} marked {rsvp.get_check_in_status_display()} — email sent to {rsvp.member.email}.',
        )
    else:
        messages.success(request, f'{rsvp.member.name} marked {rsvp.get_check_in_status_display()}.')
        messages.warning(request, f'Status email to {rsvp.member.email} failed to send — check the mail server logs.')

    return redirect(f'{reverse("custom_admin:event_check_in", args=[rsvp.event.slug])}?token={rsvp.check_in_token}')


# --- Schedule slots ----------------------------------------------------------

@staff_required
def schedule_slot_create(request, slug):
    event = get_object_or_404(Event, slug=slug)
    if request.method == 'POST':
        form = ScheduleSlotForm(request.POST, event=event)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.event = event
            slot.save()
            messages.success(request, f'Schedule slot "{slot.title}" added.')
            return redirect('custom_admin:event_detail', slug=event.slug)
    else:
        next_order = (event.schedule_slots.aggregate(m=Max('order'))['m'] or 0) + 1
        form = ScheduleSlotForm(event=event, initial={'order': next_order})
    return render(request, 'custom_admin/events/schedule_form.html', {
        'form': form,
        'event': event,
        'mode': 'create',
        'page_title': f'Add slot · {event.name}',
    })


@staff_required
def schedule_slot_edit(request, pk):
    slot = get_object_or_404(ScheduleSlot.objects.select_related('event'), pk=pk)
    if request.method == 'POST':
        form = ScheduleSlotForm(request.POST, instance=slot, event=slot.event)
        if form.is_valid():
            form.save()
            messages.success(request, f'Schedule slot "{slot.title}" updated.')
            return redirect('custom_admin:event_detail', slug=slot.event.slug)
    else:
        form = ScheduleSlotForm(instance=slot, event=slot.event)
    return render(request, 'custom_admin/events/schedule_form.html', {
        'form': form,
        'event': slot.event,
        'slot': slot,
        'mode': 'edit',
        'page_title': f'Edit slot · {slot.title}',
    })


@staff_required
def schedule_slot_delete(request, pk):
    slot = get_object_or_404(ScheduleSlot.objects.select_related('event'), pk=pk)
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    event_slug = slot.event.slug
    title = slot.title
    slot.delete()
    messages.success(request, f'Schedule slot "{title}" removed.')
    return redirect('custom_admin:event_detail', slug=event_slug)
