from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import MemberJoinForm, MemberLookupForm
from .models import Event, Member, Organizer, Page


def index(request):
    return render(request, 'index.html')


def events(request):
    upcoming = Event.objects.filter(date__gte=timezone.now())
    past = Event.objects.filter(date__lt=timezone.now()).order_by('-date')
    return render(request, 'events.html', {'upcoming': upcoming, 'past': past})


def membership(request):
    return render(request, 'membership.html')


def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug)
    return render(request, 'event_detail.html', {'event': event})


def team(request):
    organizers = Organizer.objects.all()
    return render(request, 'team.html', {'organizers': organizers})


def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug)
    return render(request, 'page.html', {'page': page})


def join(request):
    if request.method == 'POST':
        form = MemberJoinForm(request.POST)
        if form.is_valid():
            member = form.save()
            return redirect('app:join_success', member_id=member.member_id)
    else:
        form = MemberJoinForm()
    return render(request, 'join.html', {'form': form})


def join_success(request, member_id):
    member = Member.objects.filter(member_id=member_id).first()
    if not member:
        return redirect('app:join')
    return render(request, 'join_success.html', {'member': member})


def send_member_id(request, member_id):
    member = Member.objects.filter(member_id=member_id).first()
    if not member:
        messages.error(request, 'Member not found.')
        return redirect('app:join')

    send_mail(
        subject=f'Your Django Mombasa Member ID — {member.member_id}',
        message=(
            f'Hi {member.name},\n\n'
            f'Welcome to Django Mombasa! Here are your membership details:\n\n'
            f'Member ID: {member.member_id}\n'
            f'Name: {member.name}\n'
            f'Email: {member.email}\n\n'
            f'Keep this email for your records.\n\n'
            f'Learn. Build. Share. Grow.\n'
            f'— Django Mombasa'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[member.email],
    )

    messages.success(request, f'Your member ID has been sent to {member.email}.')
    return redirect('app:join_success', member_id=member.member_id)


def lookup(request):
    member = None
    searched = False

    if request.method == 'POST':
        form = MemberLookupForm(request.POST)
        searched = True
        if form.is_valid():
            member = form.lookup()
    else:
        form = MemberLookupForm()

    return render(request, 'lookup.html', {
        'form': form,
        'member': member,
        'searched': searched,
    })


def request_details(request, member_id):
    member = Member.objects.filter(member_id=member_id).first()
    if not member:
        messages.error(request, 'Member not found.')
        return redirect('app:lookup')

    send_mail(
        subject=f'Data Request — {member.member_id}',
        message=(
            f'Member {member.name} ({member.member_id}) has requested '
            f'a copy of their full membership details.\n\n'
            f'Email: {member.email}\n'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.EMAIL_HOST_USER],
    )

    send_mail(
        subject='Your Data Request — Django Mombasa',
        message=(
            f'Hi {member.name},\n\n'
            f'We have received your request for a copy of your membership details '
            f'(Member ID: {member.member_id}). We will get back to you shortly.\n\n'
            f'Thank you,\nDjango Mombasa'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[member.email],
    )

    messages.success(request, 'Your request for full details has been sent. Check your email.')
    return redirect('app:lookup')


def request_deletion(request, member_id):
    member = Member.objects.filter(member_id=member_id).first()
    if not member:
        messages.error(request, 'Member not found.')
        return redirect('app:lookup')

    send_mail(
        subject=f'Data Deletion Request — {member.member_id}',
        message=(
            f'Member {member.name} ({member.member_id}) has requested '
            f'deletion of their membership data.\n\n'
            f'Email: {member.email}\n'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.EMAIL_HOST_USER],
    )

    send_mail(
        subject='Data Deletion Request — Django Mombasa',
        message=(
            f'Hi {member.name},\n\n'
            f'We have received your request to delete your membership data '
            f'(Member ID: {member.member_id}). We will process this and get back to you.\n\n'
            f'Thank you,\nDjango Mombasa'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[member.email],
    )

    messages.success(request, 'Your deletion request has been sent. Check your email for confirmation.')
    return redirect('app:lookup')
