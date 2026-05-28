from django import forms
from django_summernote.widgets import SummernoteWidget

from events_and_activities.models import Event, ScheduleSlot, SpeakerProposal
from membership.models import Member


AUDIENCE_CHOICES = [
    ('members', 'All community members'),
    ('members_subscribed', 'Members opted in to email communications'),
    ('rsvps', 'Event RSVPs (members + guests)'),
    ('speakers', 'Speaker proposers'),
    ('speakers_approved', 'Approved speakers'),
    ('volunteers', 'Volunteer signups'),
    ('volunteers_approved', 'Approved volunteers'),
]


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'name',
            'date',
            'tags',
            'rsvp_link',
            'details',
            'has_rsvp',
            'rsvp_capacity',
            'rsvp_deadline',
            'has_cfp',
            'has_cfv',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'rsvp_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'details': SummernoteWidget(),
            'has_rsvp': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'rsvp_capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Leave blank for unlimited'}),
            'rsvp_deadline': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'has_cfp': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_cfv': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['rsvp_deadline'].input_formats = ['%Y-%m-%dT%H:%M']


class ScheduleSlotForm(forms.ModelForm):
    class Meta:
        model = ScheduleSlot
        fields = [
            'title',
            'summary',
            'order',
            'start_time',
            'end_time',
            'speaker_proposal',
            'manual_speaker_name',
            'manual_speaker_bio',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'start_time': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'end_time': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'speaker_proposal': forms.Select(attrs={'class': 'form-select'}),
            'manual_speaker_name': forms.TextInput(attrs={'class': 'form-control'}),
            'manual_speaker_bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, event=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event or (self.instance.event if self.instance and self.instance.pk else None)
        self.fields['start_time'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['end_time'].input_formats = ['%Y-%m-%dT%H:%M']
        if self.event is not None:
            self.fields['speaker_proposal'].queryset = SpeakerProposal.objects.filter(
                event=self.event,
                status=SpeakerProposal.Status.APPROVED,
            )
        else:
            self.fields['speaker_proposal'].queryset = SpeakerProposal.objects.filter(
                status=SpeakerProposal.Status.APPROVED,
            )
        self.fields['speaker_proposal'].empty_label = '— No linked speaker —'

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('speaker_proposal') and cleaned.get('manual_speaker_name'):
            raise forms.ValidationError('Pick a speaker proposal OR fill the manual speaker name, not both.')
        return cleaned


class MemberAdminForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            'name',
            'email',
            'phone',
            'gender',
            'year_of_birth',
            'experience_level',
            'primary_language',
            'kind',
            'receive_regular_updates',
            'receive_email_communications',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'year_of_birth': forms.NumberInput(attrs={'class': 'form-control', 'min': 1900, 'max': 2100}),
            'experience_level': forms.Select(attrs={'class': 'form-select'}),
            'primary_language': forms.Select(attrs={'class': 'form-select'}),
            'kind': forms.Select(attrs={'class': 'form-select'}),
            'receive_regular_updates': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'receive_email_communications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BroadcastForm(forms.Form):
    audience = forms.ChoiceField(
        choices=AUDIENCE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Who should receive this message?',
    )
    event = forms.ModelChoiceField(
        queryset=Event.objects.all().order_by('-date'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='— No event (general) —',
        help_text='Scope per-event audiences (RSVPs, speakers, volunteers) to one event.',
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject line'}),
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Write your message…'}),
        help_text='Plain text. Line breaks are preserved.',
    )
    confirm = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I have reviewed the recipient list and the message body.',
    )

    def clean(self):
        cleaned = super().clean()
        audience = cleaned.get('audience')
        event = cleaned.get('event')
        event_required = {'rsvps', 'speakers', 'speakers_approved', 'volunteers', 'volunteers_approved'}
        if audience in event_required and not event:
            self.add_error('event', 'Choose an event for this audience.')
        return cleaned
