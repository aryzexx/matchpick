from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import CompetitionGroup


User = get_user_model()


def find_invite_group(invite_code, error_message):
    invite_code = invite_code.strip()

    group = CompetitionGroup.objects.filter(
        invite_code__iexact=invite_code
    ).first()

    if group is None:
        raise forms.ValidationError(error_message)

    return invite_code, group


class RegisterForm(UserCreationForm):
    invite_code = forms.CharField(
        label="League invite code",
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter invite code",
                "autocomplete": "off",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("username",)

    def clean_invite_code(self):
        invite_code, group = find_invite_group(
            self.cleaned_data["invite_code"],
            "This invite code is not valid.",
        )
        self.invite_group = group
        return invite_code


class JoinLeagueForm(forms.Form):
    invite_code = forms.CharField(
        label="League code",
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter league code",
                "autocomplete": "off",
            }
        ),
    )

    def clean_invite_code(self):
        invite_code, group = find_invite_group(
            self.cleaned_data["invite_code"],
            "This league code is not valid.",
        )
        self.invite_group = group
        return invite_code
