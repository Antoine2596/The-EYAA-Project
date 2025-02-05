from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, ROLE_CHOICES

class CustomUserCreationForm(UserCreationForm):
    requested_role = forms.ChoiceField(choices=ROLE_CHOICES, required=False, label="Rôle souhaité")

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "requested_role",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = "Adresse email"
        self.fields["password1"].label = "Mot de passe"
        self.fields["password2"].label = "Confirmation du mot de passe"
        self.fields["password1"].help_text = None
        self.fields["password2"].help_text = None

        # https://stackoverflow.com/questions/46945449/how-to-edit-usercreationform-password-help-text
