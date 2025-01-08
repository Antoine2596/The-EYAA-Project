from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib import admin

class Genome(models.Model):
    genome_id = models.CharField(max_length=20, primary_key = True)

    # Only ACGT or ACGU, peut être mettre quelque chose pour vérifier la condition plus tard
    genome_sequence = models.TextField()

    TYPE_CHOICES = [("DNA", "ADN"), ("RNA", "ARN")]
    genome_type = models.CharField(max_length=3, choices=TYPE_CHOICES)

    organism = models.CharField(max_length=20)

    is_annotated = models.BooleanField(default=False)

    def __str__(self):
        return self.genome_id
    

class Sequence(models.Model):
    sequence_id = models.CharField(max_length=20, primary_key=True)
    dna_sequence = models.TextField()
    aa_sequence = models.TextField()
    num_chromosome = models.IntegerField(max_length=2)
    sequence_start = models.IntegerField(max_length=10)
    sequence_stop = models.IntegerField(max_length=10)
    sequence_length = models.IntegerField(max_length=10)
    gene_name = models.CharField(max_length=20)

    STATUS_CHOICES = [("Nothing", "Non-annotée"), ("Assigned", "Attribuée"),
                    ("Awaiting validation", "En attente de validation"), ("Validated", "Validée")]
    
    sequence_status = models.CharField(max_length=50, choices=STATUS_CHOICES)


class Annotation(models.Model):
    annotation_id = models.CharField(max_length=20)
    annotation_text = models.TextField() # Définir un max ?
    annotation_author = models.CharField(max_length=50)




class Domaine(models.Model):
    domain_id = models.CharField(max_length=20)
    domain_name = models.CharField(max_length=20)

    domain_start = models.IntegerField(max_length=10)
    domain_stop = models.IntegerField(max_length=10)
    domain_length = models.IntegerField(max_length=10)
    
    domain_function = models.CharField(max_length=50)

# Pas fini