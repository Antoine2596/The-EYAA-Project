from import_export import resources
from .models import Genome, Sequence, Annotation
import re 

class GenomeResource(resources.ModelResource):
    def before_import(self, dataset, **kwargs):
        # Extraire le contenu du fichier FASTA à partir des arguments passés
        name_file = kwargs.get("name")
        fasta_content = kwargs.get('file_content')
         # Utiliser une expression régulière pour extraire les en-têtes et les séquences du fichier FASTA
        entries = re.findall(r">(.*?)\n([ACGTU\n]+)", fasta_content)

        for header, sequence in entries:
        # Découper l'en-tête pour extraire le genome_id et l'organisme
        # liste_elements = header.split() # ['Chromosome', 'dna:chromosome', 'chromosome:ASM744v1:Chromosome:1:5231428:1', 'REF']
            genome_id, *organism_parts = header.split()
            organism = " ".join(organism_parts)

            # Nettoyer la séquence en supprimant les retours à la ligne
            sequence = sequence.replace("\n", "")

            # Déterminer le type de génome (ADN ou ARN) en fonction de la présence de "T" (thymine)
            genome_type = "DNA" if "T" in sequence else "RNA"

            # Ajouter une ligne de données au dataset à importer
            dataset.append_row([genome_id, sequence, genome_type, organism, False])
            
    class Meta:
        model = Genome
        fields = ('genome_id', 'genome_sequence', 'genome_type', 'organism', 'is_annotated')
        import_id_fields = ('genome_id',)



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

