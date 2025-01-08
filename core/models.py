from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

# Create your models here.

######### ATTENTION : EXEMPLE BASIQUE DE CHATGPT QUI NE CORRESPOND PAS A CE QUE L ON VEUT ###################
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('validator', 'Validateur'),
        ('annotator', 'Annotateur'),
        ('visitor', 'Visiteur'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='visitor')

    groups = models.ManyToManyField(
        Group,
        related_name="customuser_groups",  # Ajouter un related_name unique
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_permissions",  # Ajouter un related_name unique
        blank=True,
    )

class Genome(models.Model):
    name = models.CharField(max_length=255)
    sequence = models.TextField()  # Stockage de la séquence ADN
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Annotation(models.Model):
    genome = models.ForeignKey(Genome, on_delete=models.CASCADE, related_name="annotations")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="annotations")
    annotation_data = models.TextField()  # Les données spécifiques d'annotation
    created_at = models.DateTimeField(auto_now_add=True)