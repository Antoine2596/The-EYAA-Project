from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib import admin
from django.core.validators import RegexValidator
from django import forms 


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
    num_chromosome = models.IntegerField()
    sequence_start = models.IntegerField()
    sequence_stop = models.IntegerField()
    sequence_length = models.IntegerField()
    # On peut ajouter une def() pour calculer automatiquement
    gene_name = models.CharField(max_length=20)

    STATUS_CHOICES = [("Nothing", "Non-annotée"),
                      ("Assigned", "Attribuée"),
                      ("Awaiting validation", "En attente de validation"),
                      ("Validated", "Validée")]
    sequence_status = models.CharField(max_length=50, choices=STATUS_CHOICES)

    # Relation One-to-Many avec genome
    genome = models.ForeignKey(Genome, on_delete=models.CASCADE,
                               related_name="sequences")

    def __str__(self):
        return str(self.sequence_id)


class Annotation(models.Model):
    annotation_id = models.CharField(max_length=20, primary_key=True)
    annotation_text = models.TextField()  # Définir un max ?
    annotation_author = models.CharField(max_length=50)
    # On pourrait possiblement ajouter
    # un attribut "date de création" ou de "validation"

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

