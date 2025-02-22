from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib import admin
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django import forms
from django.contrib.auth import get_user_model

# Partie Utilisateur

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class Utilisateur(models.Model):
    email = models.EmailField(unique=True)
    mot_de_passe = models.CharField(max_length=10)

ROLE_CHOICES = [
    ("lecteur", "Lecteur"),
    ("annotateur", "Annotateur"),
    ("validateur", "Validateur"),
    ("visiteur", "Visiteur"),
]

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True, primary_key=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="visiteur")
    requested_role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)  # 

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"



class Genome(models.Model):
    genome_id = models.CharField(max_length=20, primary_key=True)

    # Only ACGT or ACGU
    # peut être mettre quelque chose pour vérifier la condition plus tard
    genome_sequence = models.TextField(validators=[RegexValidator(
         regex=r"^[ACGTURYKMSWBDHVN]*$",
         message="La séquence doit être composée uniquement des caractères ACGTURYKMSWBDHVN (norme IUPAC).")])

    TYPE_CHOICES = [("DNA", "ADN"), ("RNA", "ARN")]
    genome_type = models.CharField(max_length=3, choices=TYPE_CHOICES)

    organism = models.CharField(max_length=20)

    is_annotated = models.BooleanField(default=False)

    def __str__(self):
        return str(self.genome_id)


class Sequence(models.Model):
    sequence_id = models.CharField(max_length=20, primary_key=True)
    dna_sequence = models.TextField()
    aa_sequence = models.TextField()
    sequence_start = models.IntegerField()
    sequence_stop = models.IntegerField()
    sequence_length = models.IntegerField()
    
    # On peut ajouter une def() pour calculer automatiquement
    gene_name = models.CharField(max_length=20, blank=True, null=True)
    peptide_product = models.CharField(max_length=20, blank=True, null=True)

    STATUS_CHOICES = [("Nothing", "Non-annotée"),
                      ("Assigned", "Attribuée"),
                      ("Awaiting validation", "En attente de validation"),
                      ("Validated", "Validée")]
    

    BRIN_CHOICES = [(1, "Direct"),
                    (-1, "Indirect"),
                    (0, "Unknown")]
    
    SUPPORT_CHOICES = [("plasmid","Plasmide"),
                       ("chromosome","Chromosome")]
    
    sequence_brin = models.IntegerField( choices=BRIN_CHOICES, default=0)
    sequence_status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    
    information_support = models.CharField(max_length=50, choices=SUPPORT_CHOICES)

    # Relation One-to-Many avec genome
    genome = models.ForeignKey(Genome, on_delete=models.CASCADE,
                               related_name="sequences")

    def __str__(self):
        return str(self.sequence_id)
    
    def length(self):
        return str(self.sequence_id)


class Annotation(models.Model):
    annotation_id = models.CharField(max_length=20, primary_key=True)
    annotation_text = models.TextField()  # Définir un max ?
    annotation_author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="annotations",
                                          blank=True, null=True)
    # On pourrait possiblement ajouter
    # un attribut "date de création" ou de "validation"
    is_validated = models.BooleanField(default=False)
    rejected_comment = models.TextField(blank=True, null=True)
    validation_date = models.DateTimeField(blank=True, null=True)

    # Relation One-to-zero-or-one avec sequence
    sequence = models.OneToOneField(Sequence, on_delete=models.CASCADE,
                                    related_name="annotation")

    def __str__(self):
        return str(self.annotation_id)


class Domaine(models.Model):
    domain_id = models.CharField(max_length=20, primary_key=True)
    domain_name = models.CharField(max_length=20)

    domain_start = models.IntegerField()
    domain_stop = models.IntegerField()
    domain_length = models.IntegerField()
    domain_function = models.CharField(max_length=50)

    # Relation One-to-Many avec sequence
    sequence = models.ForeignKey(Sequence, on_delete=models.CASCADE,
                                 related_name="domaines")
    # sequence.domaines.all() --> récupère tous les domaines
    # liés à la séquence X

    def __str__(self):
        return str(self.domain_id)


# Historique connexion
User = get_user_model()

class ConnectionHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(default=timezone.now)
    logout_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.login_time}"
