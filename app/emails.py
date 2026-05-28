"""
Outbound email helpers for Django Mombasa.

Centralises every notification sent by the site so subject lines, from-address,
and template wiring stay consistent. Helpers are defensive — they swallow
SMTP errors with a log message so a transient mailer outage never breaks the
user's web request (and the operator can re-send from the admin if needed).
"""

from __future__ import annotations

import base64
import io
import logging
from typing import Iterable, Sequence

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def _site_url() -> str:
    return getattr(settings, 'SITE_URL', '').rstrip('/')


def _absolute(path: str) -> str:
    base = _site_url()
    if not base:
        return path
    if not path.startswith('/'):
        path = '/' + path
    return f'{base}{path}'


def _event_url(event) -> str:
    return _absolute(reverse('events_and_activities:event_detail', args=[event.slug]))


def _send(
    subject: str,
    template_base: str,
    context: dict,
    recipients: Sequence[str],
    *,
    reply_to: Sequence[str] | None = None,
    connection=None,
) -> bool:
    """Render `<template_base>.txt` (+ optional .html) and send to recipients.

    Returns True on success, False on failure (failures are logged, never raised).
    """
    recipients = [r for r in recipients if r]
    if not recipients:
        return False

    ctx = {'site_url': _site_url(), 'site_name': getattr(settings, 'SITE_NAME', 'Django Mombasa'), **context}
    try:
        text_body = render_to_string(f'{template_base}.txt', ctx)
    except Exception:
        logger.exception('Failed to render email text template %s', template_base)
        return False
    try:
        html_body = render_to_string(f'{template_base}.html', ctx)
    except Exception:
        html_body = None

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body if text_body.strip() else strip_tags(html_body or ''),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=list(recipients),
        reply_to=list(reply_to) if reply_to else None,
        connection=connection,
    )
    if html_body:
        msg.attach_alternative(html_body, 'text/html')

    try:
        msg.send(fail_silently=False)
        return True
    except Exception:
        logger.exception(
            'Failed to send email to %s (subject=%r, template=%s)',
            recipients, subject, template_base,
        )
        return False


def _generate_qr_png(payload: str) -> bytes | None:
    """Render `payload` as a PNG QR code. Returns None on failure (e.g. lib missing)."""
    try:
        import qrcode
        from qrcode.image.pil import PilImage
    except Exception:
        logger.exception('qrcode library not available')
        return None
    try:
        img = qrcode.make(payload, image_factory=PilImage, box_size=8, border=2)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()
    except Exception:
        logger.exception('Failed to render QR code for payload')
        return None


def _qr_data_uri(payload: str) -> str | None:
    """Return a `data:image/png;base64,…` URI for inline embedding (template-side fallback)."""
    data = _generate_qr_png(payload)
    if not data:
        return None
    return f'data:image/png;base64,{base64.b64encode(data).decode("ascii")}'


# --- Speaker proposal --------------------------------------------------------

def send_speaker_proposal_received(proposal) -> bool:
    return _send(
        subject=f'We received your speaker proposal for {proposal.event.name}',
        template_base='emails/speaker_proposal_received',
        context={
            'proposal': proposal,
            'event': proposal.event,
            'event_url': _event_url(proposal.event),
        },
        recipients=[proposal.email],
    )


def send_speaker_proposal_status_changed(proposal, previous_status: str | None = None) -> bool:
    status_label = proposal.get_status_display()
    return _send(
        subject=f'Your speaker proposal for {proposal.event.name}: {status_label}',
        template_base='emails/speaker_proposal_status',
        context={
            'proposal': proposal,
            'event': proposal.event,
            'event_url': _event_url(proposal.event),
            'previous_status': previous_status,
            'status_label': status_label,
        },
        recipients=[proposal.email],
    )


# --- Volunteer signup --------------------------------------------------------

def send_volunteer_signup_received(signup) -> bool:
    return _send(
        subject=f'Thanks for signing up to volunteer at {signup.event.name}',
        template_base='emails/volunteer_signup_received',
        context={
            'signup': signup,
            'event': signup.event,
            'event_url': _event_url(signup.event),
        },
        recipients=[signup.email],
    )


def send_volunteer_signup_status_changed(signup, previous_status: str | None = None) -> bool:
    status_label = signup.get_status_display()
    return _send(
        subject=f'Your volunteer application for {signup.event.name}: {status_label}',
        template_base='emails/volunteer_signup_status',
        context={
            'signup': signup,
            'event': signup.event,
            'event_url': _event_url(signup.event),
            'previous_status': previous_status,
            'status_label': status_label,
        },
        recipients=[signup.email],
    )


# --- RSVP confirmation -------------------------------------------------------

def _rsvp_check_in_url(rsvp) -> str:
    base = reverse('custom_admin:event_check_in', args=[rsvp.event.slug])
    return _absolute(f'{base}?token={rsvp.check_in_token}')


def send_rsvp_confirmation(rsvp) -> bool:
    check_in_url = _rsvp_check_in_url(rsvp)
    qr_data_uri = _qr_data_uri(check_in_url)
    return _send(
        subject=f'You\'re in: {rsvp.event.name}',
        template_base='emails/rsvp_confirmation',
        context={
            'rsvp': rsvp,
            'event': rsvp.event,
            'member': rsvp.member,
            'event_url': _event_url(rsvp.event),
            'check_in_url': check_in_url,
            'qr_data_uri': qr_data_uri,
            'has_qr': qr_data_uri is not None,
        },
        recipients=[rsvp.member.email],
    )


# --- RSVP check-in status ----------------------------------------------------

def send_rsvp_check_in_status_changed(rsvp, previous_status: str | None = None) -> bool:
    status_label = rsvp.get_check_in_status_display()
    if rsvp.check_in_status == 'accepted':
        subject = f"You're checked in: {rsvp.event.name}"
    else:
        subject = f'Update on your check-in for {rsvp.event.name}'
    return _send(
        subject=subject,
        template_base='emails/rsvp_check_in_status',
        context={
            'rsvp': rsvp,
            'event': rsvp.event,
            'member': rsvp.member,
            'event_url': _event_url(rsvp.event),
            'previous_status': previous_status,
            'status_label': status_label,
        },
        recipients=[rsvp.member.email],
    )


# --- Event reminders ---------------------------------------------------------

def send_event_reminder(event, recipients: Iterable) -> int:
    """Send the day-before reminder to a batch of Member rows.

    Returns the count of successfully-sent messages.
    """
    sent = 0
    connection = get_connection()
    try:
        connection.open()
        for member in recipients:
            ok = _send(
                subject=f'Reminder: {event.name} is tomorrow',
                template_base='emails/event_reminder',
                context={
                    'event': event,
                    'member': member,
                    'event_url': _event_url(event),
                },
                recipients=[member.email],
                connection=connection,
            )
            if ok:
                sent += 1
    finally:
        try:
            connection.close()
        except Exception:
            pass
    return sent


# --- Broadcast / custom messages --------------------------------------------

def send_broadcast(
    subject: str,
    body: str,
    recipients: Iterable[str],
    *,
    event=None,
    context_label: str | None = None,
) -> int:
    """Send a free-form message to many addresses.

    `body` is treated as plain text (rendered into the broadcast template).
    Returns the number of recipients successfully sent to.
    """
    sent = 0
    connection = get_connection()
    seen: set[str] = set()
    try:
        connection.open()
        for email in recipients:
            if not email:
                continue
            email = email.strip()
            key = email.lower()
            if not email or key in seen:
                continue
            seen.add(key)
            ok = _send(
                subject=subject,
                template_base='emails/broadcast',
                context={
                    'body': body,
                    'event': event,
                    'event_url': _event_url(event) if event else None,
                    'context_label': context_label,
                },
                recipients=[email],
                connection=connection,
            )
            if ok:
                sent += 1
    finally:
        try:
            connection.close()
        except Exception:
            pass
    return sent
