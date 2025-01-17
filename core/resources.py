from import_export import resources
from .models import Genome, Sequence, Annotation
import re 
from tablib import Dataset

import logging

logger = logging.getLogger(__name__)

class GenomeResource(resources.ModelResource):
    class Meta:
        model = Genome
        fields = ("genome_id", "genome_sequence", "genome_type", "organism", "is_annotated")
        import_id_fields = ("genome_id",)


    def before_import(self, dataset, **kwargs):
        request = kwargs.get("request")
        
        file = request.FILES.get("import_file")
        genome_id = request.POST.get("genome_id")  # Récupérer genome_id
        organism = request.POST.get("organism")   # Récupérer organism
        is_annotated = request.POST.get("is_annotated", False) #Recuperer si annnote ou pas

        fasta_content = ""
        for line in file:
            fasta_content += line.decode('utf-8')

        # Réinitialiser le dataset avec les headers corrects
        temp_dataset = Dataset()
        temp_dataset.headers = ["genome_id", "genome_sequence", "genome_type", "organism", "is_annotated"]
        

        # Utiliser une expression régulière pour extraire les en-têtes et les séquences du fichier FASTA
        entries = re.findall(r">(.*?)\n([\s\S]+?)(?=>|$)", fasta_content)
        
        for header, sequence in entries:

            # Nettoyer la séquence en supprimant les retours à la ligne
            sequence = sequence.replace("\n", "")
            
            # Déterminer le type de génome (ADN ou ARN) en fonction de la présence de "T" (thymine)
            genome_type = "DNA" if "T" in sequence else "RNA"

            
            
            # Ajouter une ligne de données au dataset à importer
            temp_dataset.append([genome_id, sequence, genome_type, organism, is_annotated])

        dataset._data = temp_dataset._data
        dataset.headers = temp_dataset.headers

        return dataset





class SequenceResource(resources.ModelResource):
    def before_import(self, dataset, **kwargs):
        # Extraire le contenu du fichier FASTA à partir des arguments passés
        name_file = kwargs.get("name")
        fasta_content = kwargs.get('file_content')
         # Utiliser une expression régulière pour extraire les en-têtes et les séquences du fichier FASTA
        entries = re.findall(r">(.*?)\n([ACGTU\n]+)", fasta_content)

        for header, sequence in entries:
            sequence_id = "id"
            dna_sequence = "AAA" 
            aa_sequence = "Z"
            num_chromosome = 1
            sequence_start = 0 
            sequence_stop = 2 
            sequence_length = 2 
            gene_name = "Test"
            sequence_status = "Nothing"
            
    class Meta:
        model = Sequence
        fields = ("sequence_id", "dna_sequence", "aa_sequence", "num_chromosome", 
                    "sequence_start", "sequence_stop", "sequence_length", "gene_name", "sequence_status")
        import_id_fields = ('sequence_id',)


class AnnotationResource(resources.ModelResource):
    def before_import(self, dataset, **kwargs):
        # Extraire le contenu du fichier FASTA à partir des arguments passés
        name_file = kwargs.get("name")
        fasta_content = kwargs.get('file_content')
         # Utiliser une expression régulière pour extraire les en-têtes et les séquences du fichier FASTA
        entries = re.findall(r">(.*?)\n([ACGTU\n]+)", fasta_content)

        for header, sequence in entries:
            annotation_id = "id"
            annotation_text = "No Annotation yet"
            annotation_author = "No author yet"
            
    class Meta:
        model = Annotation
        fields = ("annotation_id", "annotation_text", "annotation_author")
        import_id_fields = ('annotation_id',)

