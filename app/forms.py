from django import forms
from django.core.exceptions import ValidationError

from .models import Member


class MemberJoinForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            'name', 'email', 'phone', 'gender',
            'year_of_birth', 'experience_level', 'primary_language',
        ]
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
            'gender': forms.Select(attrs={
                'class': 'form-select',
            }),
            'year_of_birth': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1995',
                'min': 1940,
                'max': 2015,
            }),
            'experience_level': forms.Select(attrs={
                'class': 'form-select',
            }),
            'primary_language': forms.Select(attrs={
                'class': 'form-select',
            }),
        }


class MemberLookupForm(forms.Form):
    SEARCH_BY_CHOICES = [
        ('member_id', 'Member ID'),
        ('name_phone', 'Name + Phone'),
        ('phone_yob', 'Phone + Year of Birth'),
    ]

    search_by = forms.ChoiceField(
        choices=SEARCH_BY_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
    member_id = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'DM-000',
        }),
    )
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your full name',
        }),
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+254 700 000 000',
        }),
    )
    year_of_birth = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '1995',
        }),
    )

    def clean(self):
        cleaned = super().clean()
        method = cleaned.get('search_by')

        if method == 'member_id' and not cleaned.get('member_id'):
            raise ValidationError('Please enter your Member ID.')
        elif method == 'name_phone':
            if not cleaned.get('name') or not cleaned.get('phone'):
                raise ValidationError('Please enter both your name and phone number.')
        elif method == 'phone_yob':
            if not cleaned.get('phone') or not cleaned.get('year_of_birth'):
                raise ValidationError('Please enter both your phone number and year of birth.')

        return cleaned

    def lookup(self):
        method = self.cleaned_data['search_by']

        if method == 'member_id':
            return Member.objects.filter(
                member_id__iexact=self.cleaned_data['member_id'],
            ).first()
        elif method == 'name_phone':
            return Member.objects.filter(
                name__iexact=self.cleaned_data['name'],
                phone=self.cleaned_data['phone'],
            ).first()
        elif method == 'phone_yob':
            return Member.objects.filter(
                phone=self.cleaned_data['phone'],
                year_of_birth=self.cleaned_data['year_of_birth'],
            ).first()
        return None
