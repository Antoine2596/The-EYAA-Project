from import_export import resources
from .models import Genome, Sequence, Annotation
import re 
from tablib import Dataset

import logging

from django.db import transaction




class GenomeResource(resources.ModelResource):
    class Meta:
        model = Genome
        fields = ("genome_id", "genome_sequence", "genome_type", "organism", "is_annotated")
        import_id_fields = ("genome_id",)
        store_instance = True
        use_transactions = False 
        dry_run = True


    def before_import(self, dataset, *args, **kwargs):

        request = kwargs.get("request")
        
        file = request.FILES.get("import_file")
        genome_id = request.POST.get("genome_id")  # Récupérer genome_id
        organism = request.POST.get("organism")   # Récupérer organism
        is_annotated = request.POST.get("is_annotated") #Recuperer si annnote ou pas

        if is_annotated:
            is_annotated = True
        else:
            is_annotated = False

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

        


    def import_row(self, row, instance_loader, **kwargs):
        try:
            instance = super().import_row(row, instance_loader, **kwargs)
            print(row)
            print(f"Instance traitée : {instance}")
            return instance
        except Exception as e:
            print(f"Erreur lors du traitement de la ligne : {e}")
            return None
        
    def before_save_instance(self, instance, row, **kwargs):
        print("Avant sauvegarde :")
        print(f"Ligne : {row}")
        print(f"Instance : {instance}")

    def after_save_instance(self, instance, row, **kwargs):
        try:
            super().after_save_instance(instance, row, **kwargs)
            print("Après sauvegarde :")
            print(f"Ligne : {row}")
            print(f"Instance sauvegardée : {instance}")
        except Exception as e:
            print(f"Erreur dans after_save_instance : {e}")

    def after_import(self, dataset, result, **kwargs):
        print(f"Après l'importation : {len(result.rows)} lignes traitées.")
        for row_result in result.rows:
            if row_result:
                print(f"Type d'import : {row_result.import_type}")
                print(f"Instance importée : {row_result.instance}")
            else:
                print("RowResult est None.")






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

