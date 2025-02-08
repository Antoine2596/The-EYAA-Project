from django.core.management.base import BaseCommand
from core.models import Genome, Sequence, Annotation, CustomUser
import os, time



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
        
        # 1- Recuperation du nom de tous les organismes a importer et leurs fichiers
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
                
                if f.split(".")[0].endswith("cds"):
                    dic[id]["cds"] = options['data_folder']+ "/" +f
                elif f.split(".")[0].endswith("pep"):
                    dic[id]["pep"] = options['data_folder']+ "/" + f
                else:
                    dic[id]["Genome"] = options['data_folder']+ "/" + f

            else:

                id = (name.split(".")[0]).split("_")[0]

                if id not in dic.keys():
                    dic[id] = {}
                    dic[id]["Genra"] = "Unknown"
                    dic[id]["Species"] = "Unknown"

                if f.split(".")[0].endswith("cds"):
                    dic[id]["cds"] = options['data_folder']+ "/" +f
                elif f.split(".")[0].endswith("pep"):
                    dic[id]["pep"] = options['data_folder']+ "/" + f
                else:
                    dic[id]["Genome"] = options['data_folder']+ "/" + f

            
        # 2-Creation des organismes dans la base de données : Genome, puis sequence et annotation

        for k, v in dic.items():
            created = self.Create_Genome(v["Genome"], v["Genra"], v["Species"], k, options['mode'])  
            
            if created:
                self.Create_Sequence(v["cds"], v["pep"], created)

        # 3 - Creation des comptes

        CustomUser.objects.create_user(email = "lecteur@gmail.fr", 
                                       role= "lecteur",
                                       first_name="Prenom",
                                       last_name="Nom",
                                       password = "lecteur")
        CustomUser.objects.create_user(email = "annotateur@gmail.fr", 
                                       role= "annotateur",
                                       first_name="Prenom",
                                       last_name="Nom",
                                       password="annotateur")
        CustomUser.objects.create_user(email = "validateur@gmail.fr", 
                                       role= "validateur",
                                       first_name="Prenom",
                                       last_name="Nom",
                                       password="validateur")
        CustomUser.objects.create_user(email = "visiteur@gmail.fr", 
                                       role= "visiteur",
                                       first_name="Prenom",
                                       last_name="Nom",
                                       password="visiteur")
        CustomUser.objects.create_superuser(email= "admin@gmail.fr", 
                                            password="admin")




    def Create_Genome(self, file, Genra, Species, id, mode):
        
        # 1 - Recupere la sequence dans le fichier fasta
        f = open(file, "r")
        lines = f.readlines()
        f.close()

        sequence = "".join(l.strip() for l in lines if not l.startswith(">"))
        type = "DNA" if "T" in sequence else "RNA"


        # 2 - Verifie si les id de genomes existent deja et agit en fonction du mode choisi
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


        # 3 - Cree les genomes dans la base de données
        genome, created = Genome.objects.get_or_create(
            genome_id=id,
                defaults={
                    "genome_sequence": sequence,
                    "genome_type": type,
                    "organism": f"{Genra} {Species}",
                    "is_annotated": False
                }
            )
        
        # 4 - Message final 
        if created:
            print(f"✅ Génome {id} créé avec succès.")
            return id
        else:
            print(f"⚠ Génome {id} existe déjà.")
            return None


    def Create_Sequence(self, cds, pep, id):

        # 1 -Recuperation des champs dans le fichier cds
        genome_id = id
        dna_sequence = None

        cds = open(cds, "r")
        cds_content = cds.readlines()
        cds.close()

        dic = {}
        for l in cds_content:
            if l.startswith(">"):
                if dna_sequence:
                    dic[id]["dna_sequence"] = dna_sequence.strip()
                    dna_sequence = None

                l = l[1:]
                parts = l.split()
                id = genome_id + "_" + parts[0]
                dic[id]={}
                dic[id]["status"] = "Nothing"

                for part in parts[1:]:
                    if ":" in part:  # Vérifie si le champ est sous forme clé:valeur
                        key, value = part.split(":", 1)
                        if key == "gene":
                            dic[id]["gene_name"] = value
                        elif key == "description": 
                            dic[id]["annotation"] = value
                            dic[id]["status"] = "Validated"
                        elif len(value.split(":"))>1 :
                            chr = value.split(":")
                            dic[id]["information_support"] = key
                            dic[id]["start"] = int(chr[2])
                            dic[id]["stop"] = int(chr[3])
                            dic[id]["length"] = abs(int(chr[3])-int(chr[2]))
                            dic[id]["brin"] = int(chr[-1])
                            if abs(dic[id]["brin"]) != 1:
                                dic[id]["brin"] = 0

                        
                        if not "gene_name" in dic[id].keys():
                            dic[id]["gene_name"] = "None"
                        if not "status" in dic[id].keys():
                             dic[id]["status"] = "Nothing"
                
            else:
                if dna_sequence: 
                    dna_sequence = dna_sequence + l
                else:
                    dna_sequence = l

        dic[id]["dna_sequence"] = dna_sequence.strip()

        # 2 -Recuperation des sequences peptidiques

        pep = open(pep, "r")
        pep_content = pep.readlines()
        pep.close()

        pep_sequence=None

        for l in pep_content:
            if l.startswith(">"):
                if pep_sequence:
                    dic[id]["pep_sequence"] = pep_sequence.strip()
                    pep_sequence = None

                l = l[1:]
                parts = l.split()
                id = genome_id + "_" + parts[0]
                
            else:
                if pep_sequence: 
                    pep_sequence = pep_sequence + l
                else:
                    pep_sequence = l

        dic[id]["pep_sequence"] = pep_sequence.strip()


        # 3 - Creation des sequences en bulk

        #print(dic)
        genome = Genome.objects.get(genome_id=genome_id)
        sequence_objects = [
            Sequence(
                sequence_id=k,
                dna_sequence=v["dna_sequence"],
                aa_sequence=v["pep_sequence"],
                information_support=v.get("information_support", None),
                sequence_start=v.get("start", None),
                sequence_stop=v.get("stop", None),
                sequence_length=v.get("length", None),
                gene_name=v.get("gene_name", "None"),
                sequence_status=v.get("status", "Nothing"),
                genome=genome,
                sequence_brin=v["brin"]
            )
            for k, v in dic.items()
        ]

        Sequence.objects.bulk_create(sequence_objects) 

        # 4 -Creation des annotations en bulk

        annotation_objects = [
            Annotation(
                annotation_id = "ANN_"+ str(k),
                annotation_text =v["annotation"],
                sequence_id = k,
                is_validated = True,
            )
            for k, v in dic.items() if "annotation" in v and v["annotation"]
        ]

        Annotation.objects.bulk_create(annotation_objects)

        # 5 - Mise a jour du genome s il est annoté : 


        if all("annotation" in v and v["annotation"] for v in dic.values()):
            genome.is_annotated = True
            genome.save()