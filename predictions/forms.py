from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import CompetitionGroup


class RegisterForm(UserCreationForm):
    """
    Registration form for MatchPick.

    Version 1 intentionally collects only:
    - username
    - password
    - invite code

    It does not collect email addresses, phone numbers, full names,
    profile photos or location data because those are not required for
    the private prediction competition to work.
    """

    invite_code = forms.CharField(
        max_length=30,
        label="Invite code",
        help_text="Enter the invite code shared by your group organiser.",
    )

    class Meta:
        model = User
        fields = ["username", "password1", "password2", "invite_code"]

    def clean_invite_code(self):
        """
        Checks whether the invite code belongs to an existing competition group.
        """

        invite_code = self.cleaned_data["invite_code"].strip()

        try:
            self.invite_group = CompetitionGroup.objects.get(
                invite_code__iexact=invite_code
            )
        except CompetitionGroup.DoesNotExist:
            raise forms.ValidationError(
                "This invite code is not valid. Please check it and try again."
            )

        return invite_code