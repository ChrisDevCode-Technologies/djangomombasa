from django import forms
from django.core.exceptions import ValidationError

from membership.models import Member

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
            member = Member.objects.filter(email=raw).first()
        else:
            member = Member.objects.filter(member_id__iexact=raw).first()
        if member is None:
            raise ValidationError(
                'We could not find a member with that ID or email. '
                'If you are not yet a member, please join first.'
            )
        self.cleaned_member = member
        return raw


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
