from django import forms
from django.utils.translation import gettext_lazy as _

from core.models import CVLanguage, User


class LoginForm(forms.Form):
    email = forms.CharField(
        max_length=100,
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'jon@doe.com',
                'class': 'w-full rounded bg-zinc-200 focus:outline-none focus:shadow-outline px-2 py-1 focus:ring-2 ring-green-700'
            }
        )
    )
    password = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': '********',
                'class': 'w-full rounded bg-zinc-200 focus:outline-none focus:shadow-outline px-2 py-1 focus:ring-2 ring-green-700'
            }
        )
    )


class GenerateForm(forms.Form):
    brief = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={
        'class': 'resize-none'
    }))
    language = forms.ModelChoiceField(
        queryset=CVLanguage.objects.all(),
    )
    role = forms.ModelChoiceField(
        queryset=None
    )
    skills = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].queryset = user.roles.all()
        self.fields['skills'].queryset = user.skills.all()

    def clean(self):
        cleaned_data = super().clean()
        if len(cleaned_data.get('skills', [])) != 10:
            self.add_error('skills', _('You must select 10 skills'))
        return cleaned_data
