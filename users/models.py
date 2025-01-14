from django.db import models
from django.contrib.auth.models import AbstractUser

ROLE_CHOICES = [
    ("lecteur", "Lecteur"),
    ("annotateur", "Annotateur"),
    ("validateur", "Validateur"),
]

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="lecteur")
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.email} ({self.role})"
