from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin

#https://docs.djangoproject.com/en/5.1/ref/contrib/auth/
class Utilisateur(models.Model):
    email = models.EmailField(unique=True)
    mot_de_passe = models.CharField(max_length=10)
