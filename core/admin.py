from django.contrib import admin
from django import forms
from import_export.forms import ImportForm, ConfirmImportForm
from .models import Genome, Sequence, Annotation
from import_export.formats.base_formats import DEFAULT_FORMATS


from import_export.admin import ImportMixin
from .resources import GenomeResource, SequenceResource, AnnotationResource  
from .models import CustomUser, ConnectionHistory
from django.db.models.signals import post_save
from django.dispatch import receiver


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "role", "requested_role", "is_staff", "is_superuser", "last_login")
    search_fields = ("email", "first_name", "last_name", "role", "requested_role")
    list_editable = ("role",) 



# Formulaire pour recuperer manuellement l id et le nom du genome 

class GenomeImportForm(ImportForm):
    genome_id = forms.CharField(required=True, label="Identifiant unique du génome sur les bases de données")
    organism = forms.CharField(required=True, label="Genre et espece du génome") 
    is_annotated = forms.BooleanField(required=False, label="Déjà annoté", initial=False) 
    import_file = forms.FileField(required=True, label="Fichier FASTA à importer")

    
    def clean(self):
        cleaned_data = super().clean()

        genome_id = self.cleaned_data.get("genome_id")
        if Genome.objects.filter(genome_id=genome_id).exists():
            raise forms.ValidationError(f"Un génome avec l'ID '{genome_id}' existe déjà dans la base de données.")
        
        # Récupérer les valeurs du formulaire
        self.genome_id = cleaned_data.get('genome_id')
        self.organism = cleaned_data.get('organism')
        self.is_annotated = cleaned_data.get('is_annotated')
        return cleaned_data
    

class GenomeAdmin(ImportMixin, admin.ModelAdmin):
    resource_class = GenomeResource  # Lien avec la ressource
    import_form_class = GenomeImportForm
    
    list_display = ("genome_id", "organism", "genome_type", "is_annotated") #Les champs a Monterr
    list_filter = ("genome_type", "is_annotated") #Admin peut trier par ces champs les genomes de la base
    search_fields = ("genome_id", "organism") #Admin peut rechercher par ces champs les genomes de la base
    list_editable = ("is_annotated",)   #Champ modifiable par l'admin

     # Autorise l'ajout manuel de génomes
    def has_add_permission(self, request):
        return True


admin.site.register(Genome, GenomeAdmin)

@admin.register(Sequence)
class SequenceAdmin(ImportMixin, admin.ModelAdmin):
    resource_class = SequenceResource  # Lien avec la ressource

    list_display = ("sequence_id", "information_support",
                    "sequence_start", "sequence_stop", "sequence_length", "gene_name", "sequence_status") 
    list_filter = ("information_support", "sequence_status") 
    search_fields = ("sequence_id", "dna_sequence","aa_sequence", "gene_name",) 

     # Empêche l'ajout manuel de génomes
    def has_add_permission(self, request):
        return True

@admin.register(Annotation)
class AnnotationAdmin(ImportMixin, admin.ModelAdmin):
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

@receiver(post_save, sender=CustomUser)
def update_user_session(sender, instance, **kwargs):
    from django.contrib.sessions.models import Session
    from django.utils import timezone

    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    for session in sessions:
        data = session.get_decoded()
        if data.get('_auth_user_id') == str(instance.pk):
            session.modified = True