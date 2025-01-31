from django.core.management.base import BaseCommand
from core.models import Genome, Sequence, Annotation
import os 


class Command(BaseCommand):
    help = "Importation en bulk des donnees depuis un repertoire contant les fasta du genome, des CDS et des proteines"

    def add_arguments(self, parser):
        parser.add_argument('data_folder', type=str, help="Chemin du repertoire contenant les donnees a importer")
        parser.add_argument("mode",
                            type=str,
                            choices=["k", "r", "i"],
                            help="Action à effectuer si un génome existe déjà : k : keep both, r : replace ou i : ignore"
                            )
    def handle(self, *args, **options):
        files = os.listdir(options['data_folder'])
        
        # 1- Recuperationd de tous les organismes a importer et stockage dans un dictionnaire

        dic = {}

        for f in files: 
            name = f.split(".")[0]
            if name.split("_")[-1] == "cds" or name.split("_")[-1] == "pep":
                name = "_".join(name.split("_")[:-1])
            

            if len(name.split("_")) >= 3:
                id = "_".join(name.split("_")[2:])

                if id not in dic.keys():
                    dic[id] = {}
                    dic[id]["Genra"] = name.split("_")[0]
                    dic[id]["Species"] = name.split("_")[1]
                
                if f.split("_")[-1] == "cds.fa":
                    dic[id]["cds"] = options['data_folder']+ "/" +f
                elif f.split("_")[-1] == "pep.fa":
                    dic[id]["pep"] = options['data_folder']+ "/" + f
                else:
                    dic[id]["Genome"] = options['data_folder']+ "/" + f

            else:
                print("Erreur avec le fichier ", f , "\n Les noms de fichiers doivent respecter le format suivant : Genre_Espece_id \n Pour les fichiers de cds ou de proteines ils doivent finir par _pep ou _cds ")
            
        # 2-Creation des organismes dans la base de données 

        for k in dic.keys():
            self.Create_Genome(dic[k]["Genome"], dic[k]["Genra"], dic[k]["Species"], k, options['mode'])    

    def Create_Genome(self, file, Genra, Species, id, mode):

        f = open(file, "r")
        lines = f.readlines()
        f.close()

        sequence = "".join(l.strip() for l in lines if not l.startswith(">"))
            
        type = "DNA" if "T" in sequence else "RNA"

        existing_genome = Genome.objects.filter(genome_id=id)

        if existing_genome:
            if mode == "i":
                print(f"⚠ Génome {id} existe déjà. IGNORÉ.")
                return

            elif mode == "r":
                existing_genome.delete()
                print(f"🔄 Génome {id} remplacé.")

            elif mode == "k":
                # Générer un nouvel ID unique
                new_id = f"{id}.1"
                while Genome.objects.filter(genome_id=new_id).exists():
                    new_id += ".1"  # Ajoute "_new" jusqu'à ce qu'on ait un ID unique
                id = new_id
                print(f"🆕 Génome {id} créé en plus du précédent.")


        genome, created = Genome.objects.get_or_create(
            genome_id=id,
                defaults={
                    "genome_sequence": sequence,
                    "genome_type": type,
                    "organism": f"{Genra} {Species}",
                    "is_annotated": False
                }
            )

        if created:
            print(f"✅ Génome {id} créé avec succès.")
        else:
            print(f"⚠ Génome {id} existe déjà.")

    
    def Create_Sequence(self):
        return 0
    
    def Create_Annotation(self):
        return 0
