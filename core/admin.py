from django.contrib import admin
from import_export import resources

from .models import Genome, Sequence, Annotation, ConnectionHistory


from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Genome
from .resources import GenomeResource, SequenceResource, AnnotationResource  
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("email", "role", "is_staff", "is_superuser", "last_login")
    search_fields = ("email",)

@admin.register(Genome)
class GenomeAdmin(ImportExportModelAdmin):
    resource_class = GenomeResource  # Lien avec la ressource
    list_display = ("genome_id", "organism", "genome_type", "is_annotated") #Les champs a Recuperer 
    list_filter = ("genome_type", "is_annotated") #Admin peut trier par ces champs les genomes de la base
    search_fields = ("genome_id", "organism") #Admin peut rechercher par ces champs les genomes de la base
    list_editable = ("is_annotated",)   #Champ modifiable par l'admin

     # Empêche l'ajout manuel de génomes
    def has_add_permission(self, request):
        return True
    

@admin.register(Sequence)
class SequenceAdmin(ImportExportModelAdmin):
    resource_class = SequenceResource  # Lien avec la ressource


    list_display = ("sequence_id", "dna_sequence", "aa_sequence", "num_chromosome", 
                    "sequence_start", "sequence_stop", "sequence_length", "gene_name", "sequence_status") #Les champs a Recuperer 
    list_filter = ("num_chromosome", "sequence_start", "sequence_stop", "sequence_length", "sequence_status") 
    search_fields = ("sequence_id", "dna_sequence","aa_sequence", "gene_name") 

     # Empêche l'ajout manuel de génomes
    def has_add_permission(self, request):
        return True
    
@admin.register(Annotation)
class AnnotationAdmin(ImportExportModelAdmin):
    resource_class = AnnotationResource  # Lien avec la ressource


    list_display = ("annotation_id", "annotation_text", "annotation_author")
    search_fields = ("annotation_id", "annotation_text", "annotation_author")

     # Empêche l'ajout manuel de génomes
    def has_add_permission(self, request):
        return True
    
@admin.register(ConnectionHistory)
class ConnectionHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'logout_time')
    list_filter = ('user', 'login_time')