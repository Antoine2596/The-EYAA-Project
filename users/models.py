from django.db import models
from django.contrib.auth.models import AbstractUser

# Exemple d’options pour le champ "role"
ROLE_CHOICES = [
    ("lecteur", "Lecteur"),
    ("annotateur", "Annotateur"),
    ("validateur", "Validateur"),
]

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="lecteur")

    # L’email devient le champ principal pour s’identifier
    USERNAME_FIELD = "email"

    # Champs obligatoires en plus de l'email
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    def __str__(self):
        return f"{self.email} - {self.role}"
