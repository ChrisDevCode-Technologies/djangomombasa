from django import forms
from django.core.exceptions import ValidationError

from membership.models import Member, RSVPGuest

from .models import SpeakerProposal, VolunteerSignup


class RSVPForm(forms.Form):
    member_identifier = forms.CharField(
        label='Member ID or email',
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'DM-042 or you@example.com',
            'autocomplete': 'off',
        }),
    )

    def clean_member_identifier(self):
        raw = (self.cleaned_data.get('member_identifier') or '').strip()
        if not raw:
            raise ValidationError('Please enter your Member ID or email.')
        if '@' in raw:
            member = Member.objects.filter(email=raw, kind=Member.Kind.MEMBER).first()
        else:
            member = Member.objects.filter(member_id__iexact=raw, kind=Member.Kind.MEMBER).first()
        if member is None:
            raise ValidationError(
                'We could not find a member with that ID or email. '
                'If you are not yet a member, please RSVP as a guest below or join the community.'
            )
        self.cleaned_member = member
        return raw


class RSVPGuestForm(forms.Form):
    name = forms.CharField(
        label='Full name',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your full name',
        }),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'you@example.com',
        }),
    )
    receive_email_communications = forms.BooleanField(
        label='Email me about future events and announcements',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
    )

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip()
        if not email:
            raise ValidationError('Please enter your email.')
        # Resolve to existing person (member or prior guest) by email; otherwise leave None.
        existing = Member.objects.filter(email__iexact=email).first()
        self.existing_member = existing
        return email

    def resolve_or_create_guest(self):
        """Return a Member row (existing or freshly-created RSVPGuest) for this submission."""
        existing = getattr(self, 'existing_member', None)
        if existing is not None:
            if self.cleaned_data.get('receive_email_communications') and not existing.receive_email_communications:
                existing.receive_email_communications = True
                existing.save(update_fields=['receive_email_communications'])
            return existing
        guest = RSVPGuest(
            name=self.cleaned_data['name'],
            email=self.cleaned_data['email'],
            receive_email_communications=self.cleaned_data.get('receive_email_communications', False),
        )
        guest.save()
        return guest


class SpeakerProposalForm(forms.ModelForm):
    class Meta:
        model = SpeakerProposal
        fields = ['name', 'email', 'proposed_talk_title', 'talk_abstract', 'bio']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'you@example.com',
            }),
            'proposed_talk_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Title of your proposed talk',
            }),
            'talk_abstract': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'What is your talk about? Who is it for? What will attendees learn?',
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'A short bio (optional)',
            }),
        }


class VolunteerSignupForm(forms.ModelForm):
    class Meta:
        model = VolunteerSignup
        fields = ['name', 'email', 'phone', 'availability', 'skills_or_role']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'you@example.com',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+254 700 000 000',
            }),
            'availability': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'When are you available? (e.g. setup day, event day mornings)',
            }),
            'skills_or_role': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. registration desk, AV support, photography',
            }),
        }
