from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render

from .forms import MemberJoinForm, MemberLookupForm
from .models import Member


def membership(request):
    return render(request, 'membership/membership.html')


def join(request):
    if request.method == 'POST':
        form = MemberJoinForm(request.POST)
        if form.is_valid():
            member = form.save()
            return redirect('membership:join_success', member_id=member.member_id)
    else:
        form = MemberJoinForm()
    return render(request, 'membership/join.html', {'form': form})


def join_success(request, member_id):
    member = Member.objects.filter(member_id=member_id).first()
    if not member:
        return redirect('membership:join')
    return render(request, 'membership/join_success.html', {'member': member})


def send_member_id(request, member_id):
    member = Member.objects.filter(member_id=member_id).first()
    if not member:
        messages.error(request, 'Member not found.')
        return redirect('membership:join')

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
    return redirect('membership:join_success', member_id=member.member_id)


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

    return render(request, 'membership/lookup.html', {
        'form': form,
        'member': member,
        'searched': searched,
    })


def request_details(request, member_id):
    member = Member.objects.filter(member_id=member_id).first()
    if not member:
        messages.error(request, 'Member not found.')
        return redirect('membership:lookup')

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
    return redirect('membership:lookup')


def request_deletion(request, member_id):
    member = Member.objects.filter(member_id=member_id).first()
    if not member:
        messages.error(request, 'Member not found.')
        return redirect('membership:lookup')

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
    return redirect('membership:lookup')
