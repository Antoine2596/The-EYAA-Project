from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from .form_inscription import CustomUserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from .models import CustomUser
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from django.contrib import messages
from .models import Genome, Sequence, Annotation
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from django.utils.timezone import now
from django.core.paginator import Paginator
from django.db.models import Count

from django.shortcuts import redirect



from django.http import HttpResponse
#from import_export.formats.base import BaseFormat
from .resources import GenomeResource
from .admin import GenomeImportForm
import csv



##############
# Fonction pour accès
#############
# Fonction pour gérer l'accès
def role_required(role1, role2=None, role3=None):
    def decorator(view_func):
        def wrapper(request):
            if request.user.is_authenticated:  # Vérifie si l'utilisateur est connecté
                user_role = request.user.role
                if user_role in [role1, role2, role3]:  # Vérifie le rôle
                    return view_func(request)
            return redirect('access_denied')  # Redirection si non connecté ou mauvais rôle
        return wrapper
    return decorator

# Page pour les accès refusés
def access_denied(request):
    return render(request, "core/access_denied.html")

# Page d'accueil
def page_non_connecte(request):
    return render(request, "core/home.html")

# Accès public (pas de restriction)
def home(request):
    return render(request, "core/home.html")

# Accès restreint à certains rôles
def contacts(request):
    return render(request, "core/contacts.html")


# @login_required
@role_required("lecteur", "annotateur", "validateur")
def profile(request):
    return render(request, "core/profile.html")

@login_required
def profile_informations(request):
    
    validated_count = Annotation.objects.filter(annotation_author=request.user, is_validated=True).count()
    awaiting_count = Annotation.objects.filter(annotation_author=request.user, is_validated=False, sequence__sequence_status="Awaiting validation").count()
    assigned_count = Annotation.objects.filter(annotation_author=request.user, is_validated=False, sequence__sequence_status="Assigned").count()

    return render(request, 'core/profile_informations.html', {
        'validated_count': validated_count,
        'awaiting_count': awaiting_count,
        'assigned_count': assigned_count,
    })

@login_required
def profile_change_PSWD(request):

    if request.method == "POST":
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Important pour éviter la déconnexion
            messages.success(request, "Votre mot de passe a été mis à jour avec succès.")
            return redirect("profile")  # Redirige vers le profil après changement
    else:
        password_form = PasswordChangeForm(request.user)  # Lier le form à l'utilisateur connecté

    return render(request, "core/profile_change_PSWD.html", {"password_form": password_form})

@login_required
def profile_annotations(request):
    status_filter = request.GET.get("filter", "all")
    annotations = Annotation.objects.filter(annotation_author=request.user)
    page_number = request.GET.get("page", 1)

    if status_filter == "validated":
        annotations = annotations.filter(is_validated=True)
    elif status_filter == "awaiting":
        annotations = annotations.filter(is_validated=False, sequence__sequence_status = "Awaiting validation")
    elif status_filter == "assigned":
        annotations = annotations.filter(is_validated=False, sequence__sequence_status = "Assigned")

    annotations_count = annotations.count()

    paginator = Paginator(annotations, 2)
    annotations_page = paginator.get_page(page_number)

    return render(request, 'core/profile_annotations.html', {'annotations': annotations_page,'status_filter': status_filter,
        'annotations_count': annotations_count})


def Pageinscription(request):
    return render(request, "core/inscription.html")

def deconnexion(request):
    logout(request)
    return redirect("home")


@login_required
def visualisation(request, obj_type, obj_id):
    page_obj = None  # Définition par défaut
    search_query = None  # Définition par défaut
    if obj_type == "genome":
        obj = get_object_or_404(Genome, genome_id=obj_id)
        # récupère les CDS associées au génome
        associated_sequences = obj.sequences.all()

        # récupère le paramètre de recherche si spécifié
        search_query = request.GET.get('search', '')

        if search_query:
            # pour faire la recherche par nom de gène 
            associated_sequences = associated_sequences.filter(
                Q(gene_name__icontains=search_query)
            )

        # pagination : 20 CDS par page
        paginator = Paginator(associated_sequences, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)


    elif obj_type == "sequence":
        obj = get_object_or_404(Sequence, sequence_id = obj_id)
    elif obj_type == "annotation":
        obj = get_object_or_404(Annotation, annotation_id=obj_id)

        
    else:
        return render(request, "core/404.html", {"message": "Type d'objet non reconnu."})

    return render(
        request,
        "core/visualisation.html",
        {
            "obj": obj,
            "obj_type": obj_type,
            "page_obj": page_obj,
            "search_query": search_query,  
        },
    )



def inscription(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = "visiteur"  
            user.requested_role = form.cleaned_data.get('requested_role') 
            user.save()
            return redirect('connexion')
    else:
        form = CustomUserCreationForm()

    return render(request, "core/inscription.html", {"form": form})



def connexion(request):
    if request.method == "POST":

        email = request.POST.get("email", "")
        password = request.POST.get("password", "") 


        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Connexion réussie !")
            return redirect("home")
        else:
            messages.error(request, "Adresse email ou mot de passe incorrect.")
    return render(request, "core/connexion.html")

@role_required("lecteur", "annotateur", "validateur")
def genome_list(request):
    genomes = Genome.objects.all()  # Récupère tous les génomes
    return render(request, "test.html", {"genomes": genomes})


def is_not_visitor(user):
    return user.role != "visiteur"


@role_required("lecteur", "annotateur", "validateur")
def database_view(request):

    user_request = request.GET.get("user_request", "").strip()
    selected_type = request.GET.get("type", "genome") 
    is_annotated = request.GET.get("is_annotated") == "true"
    min_length = request.GET.get("min_length")
    max_length = request.GET.get("max_length")
    chromosome = request.GET.get("chromosome")
    sequence_type = request.GET.get("sequence_type")
    Brin = request.GET.get("Brin")


    genomes = sequences = None
    
    # Si l'utilisateur n'a pas fait de recherche, afficher le dashboard
    dashboard = not bool(user_request)


    if dashboard:
        
        total_genomes = Genome.objects.count()
        total_species = Genome.objects.values("organism").distinct().count()
        total_sequences = Sequence.objects.count()
        annotated_sequences = Annotation.objects.filter(is_validated=True).values("sequence").distinct().count()
        
        
        # Calcul de la proportion des séquences annotées
        annotation_ratio = (annotated_sequences / total_sequences * 100) if total_sequences > 0 else 0

        context = {
            "dashboard": True,
            "total_genomes": total_genomes,
            "total_species": total_species,
            "total_sequences": total_sequences,
            "annotation_ratio": annotation_ratio
        }

    else:
        if selected_type == "genome":
            genomes = Genome.objects.filter(
                (Q(genome_id__icontains=user_request) | Q(organism__icontains=user_request)) | Q(genome_sequence__icontains=user_request) 
            )
            if is_annotated:
                genomes = genomes.filter(is_annotated=True)
            

        elif selected_type == "sequence":
            
            
            sequences = Sequence.objects.filter(
                (Q(sequence_id__icontains=user_request) | 
                 Q(gene_name__icontains=user_request) | 
                 Q(dna_sequence__icontains=user_request) |
                 Q(aa_sequence__icontains=user_request) |
                 Q(genome__genome_id__icontains=user_request) | 
                 Q(genome__organism__icontains=user_request) ) |
                 Q(annotation__annotation_text__icontains=user_request)
            )
            if min_length:
                sequences = sequences.filter(sequence_length__gte=int(min_length))
            if max_length:
                sequences = sequences.filter(sequence_length__lte=int(max_length))
            if chromosome:
                sequences = sequences.filter(information_support__iexact=chromosome)
            if Brin:
                sequences = sequences.filter(sequence_brin__iexact=Brin)
            if sequence_type:
                sequences = sequences.filter(selected_type_iexact=sequence_type)
            if is_annotated:
                sequences = sequences.filter(
                    Q(sequence_status__iexact="Validated") | Q(sequence_status__iexact="Awaiting validation")
                            )

        combined_results = (
    [{"obj": obj, "type": "Genome"} for obj in genomes] if genomes else []
) + (
    [{"obj": obj, "type": "Sequence"} for obj in sequences] if sequences else []
)

        

        paginator = Paginator(combined_results, 3)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            "dashboard": False,
            "page_obj": page_obj,
            "total_genomes": len(genomes) if genomes else 0,
            "total_sequences": len(sequences) if sequences else 0,
            "selected_type": selected_type,  # Garde la sélection active
        }

    return render(request, "core/database.html", context)

# Vérifier que l'utilisateur est un validateur
def is_validator(user):
    return user.role == "validateur"


@role_required("validateur")
def annotations_listing(request):
    genomes = Genome.objects.all()
    search = request.GET.get("search", "")
    genome_filter = request.GET.get("genome", "")
    min_length = int(request.GET.get("min_length", 0))
    max_length = int(request.GET.get("max_length", 10000))
    
    filter_conditions = Q(sequence__sequence_status="Awaiting validation")
    
    if search:
        filter_conditions &= Q(sequence__sequence_id__icontains=search)
    
    if genome_filter:
        filter_conditions &= Q(sequence__genome__genome_id=genome_filter)
    
    if min_length:
        filter_conditions &= Q(sequence__sequence_length__gte=min_length)
    
    if max_length:
        filter_conditions &= Q(sequence__sequence_length__lte=max_length)

    non_validated_annotations = Annotation.objects.filter(filter_conditions)
    annotations_count = non_validated_annotations.count()

    paginator = Paginator(non_validated_annotations, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "core/annotations_non_validates.html",  {"page_obj": page_obj, "genomes": genomes, "annotations_count": annotations_count})

@user_passes_test(is_validator)
def validate_annotation(request, annotation_id):
    annotation = get_object_or_404(Annotation, annotation_id=annotation_id)
    sequence = annotation.sequence

    if request.method == "POST":
        action = request.POST.get("action")
        comment = request.POST.get("comment", "").strip()

        if action == "validate":
            annotation.is_validated = True
            annotation.validation_date = now()
            sequence.sequence_status = "Validated"
            messages.success(request, "L'annotation a été validée avec succès.")

        elif action == "reject":
            annotation.is_validated = False
            annotation.rejected_comment = comment
            sequence.sequence_status = "Assigned"
            messages.warning(request, "L'annotation a été rejetée.")

        annotation.save()
        sequence.save()
    
        return redirect("annotations_listing")
    
    return render(request, "core/validation_annotation.html", {"annotation": annotation, "user": request.user})

@user_passes_test(is_validator)
def sequences_non_assigned(request):

    genomes = Genome.objects.all()

    search = request.GET.get("search", "")
    genome_filter = request.GET.get("genome", "")
    min_length = int(request.GET.get("min_length", 0))
    max_length = int(request.GET.get("max_length", 10000))
    
    filter_conditions = Q(sequence_status="Nothing")
    
    if search:
        filter_conditions &= Q(sequence_id__icontains=search)
    
    if genome_filter:
        filter_conditions &= Q(genome__genome_id=genome_filter)
    
    if min_length:
        filter_conditions &= Q(sequence_length__gte=min_length)
    
    if max_length:
        filter_conditions &= Q(sequence_length__lte=max_length)
    
    # Appliquer le filtrage
    non_assigned_sequences = Sequence.objects.filter(filter_conditions)
    sequences_count = non_assigned_sequences.count()
    
    # Pagination
    paginator = Paginator(non_assigned_sequences, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "core/sequences_non_assigned.html", {"page_obj": page_obj, "genomes": genomes, "sequences_count": sequences_count})

@user_passes_test(is_validator)
def attribution_sequence(request, sequence_id):
    sequence_id = get_object_or_404(Sequence, sequence_id = sequence_id)
    annotateurs = CustomUser.objects.annotate(annotation_count=Count('annotations', filter=Q(annotations__is_validated=False))).filter(role__in=["annotateur", "validateur"], annotation_count__lt=5)
    
    if request.method == "POST":
        annotateur_id = request.POST.get("annotateur")
        annotateur = get_object_or_404(CustomUser, email = annotateur_id)

        Annotation.objects.create(
            annotation_id=f"ANN_{sequence_id}",
            annotation_text="",
            sequence=sequence_id,
            is_validated=False,
            annotation_author=annotateur
        )

        sequence_id.sequence_status = "Assigned"
        sequence_id.save()

        messages.success(request,  f"La séquence {sequence_id} a été attribuée à {annotateur.email}.")
        return redirect("sequences_non_assigned")

    return render(request, "core/attribution_sequence.html", {"sequence": sequence_id, "annotateurs": annotateurs})

@user_passes_test(is_validator)
def attribution_auto(request):
    non_assigned_sequences = Sequence.objects.filter(sequence_status="Nothing")

    annotateurs = CustomUser.objects.annotate(annotation_count=Count('annotations', filter=Q(annotations__is_validated=False))).filter(role__in=["annotateur", "validateur"], annotation_count__lt=5)

    if not annotateurs:
        messages.warning(request, "Aucun annotateur disponible pour l'attribution automatique.")
        return redirect("sequences_non_assigned")

    attribution_done = 0
    for sequence in non_assigned_sequences:
        annotateur = annotateurs.order_by("annotation_count").first()

        if not annotateur:
            break 

        Annotation.objects.create(
            annotation_id=f"ANN_{sequence.sequence_id}",
            annotation_text="",
            is_validated=False,
            annotation_author=annotateur,
            sequence=sequence
        )

        sequence.sequence_status = "Assigned"
        sequence.save()
        attribution_done += 1

    messages.success(request, f"{attribution_done} séquences ont été attribuées automatiquement.")
    return redirect("sequences_non_assigned")

@login_required
def annoter(request, sequence_id):
    sequence = get_object_or_404(Sequence, sequence_id=sequence_id)
    annotation = get_object_or_404(Annotation, sequence=sequence, annotation_author=request.user)

    is_editable = annotation.sequence.sequence_status == "Assigned"

    if request.method == "POST" and is_editable:
        gene_name = request.POST.get('gene_name')
        peptide_product = request.POST.get('peptide_product')
        text = request.POST.get('text')

        sequence.gene_name = gene_name
        sequence.peptide_product = peptide_product
        annotation.annotation_text = text

        if 'send_to_validation' in request.POST:
            sequence.sequence_status = "Awaiting validation"
            annotation.save()
            sequence.save()

            messages.success(request, "L'annotation a été envoyée pour validation !")
            return redirect("/profil/annotations/?success=1")
        
        
        elif "save" in request.POST:
            annotation.save()
            sequence.save()
            messages.success(request, "L'annotation a été sauvegardée avec succès.")
            return redirect("/profil/annotations/?saved=1")
        
        return redirect("profile_annotations")

    return render(
        request, 
        "core/annoter_sequence.html", 
        {
            "sequence": sequence, 
            "annotation": annotation, 
            "is_editable": is_editable
        }
    )

def extraction_view(request):

    selected_type = request.GET.get("type", "genome") 
    type = (selected_type == "genome")

    context = {
            "type": type,
    }
    return render(request, "core/extraction.html", context)


def extraction_file(request):

    # 1-Filrer les données

    user_request = request.GET.get("user_request", "").strip()
    selected_type = request.GET.get("type", "genome") 
    is_annotated = request.GET.get("is_annotated") == "true"
    min_length = request.GET.get("min_length")
    max_length = request.GET.get("max_length")
    chromosome = request.GET.get("chromosome")
    sequence_type = request.GET.get("sequence_type")
    Brin = request.GET.get("Brin")


    genomes = sequences = None
    
    if selected_type == "genome":
        genomes = Genome.objects.filter(
            (Q(genome_id__icontains=user_request) | Q(organism__icontains=user_request)) | Q(genome_sequence__icontains=user_request) 
        )
        if is_annotated:
            genomes = genomes.filter(is_annotated=True)
        

    elif selected_type == "sequence":
        sequences = Sequence.objects.filter(
                (Q(sequence_id__icontains=user_request) | 
                 Q(gene_name__icontains=user_request) | 
                 Q(dna_sequence__icontains=user_request) |
                 Q(aa_sequence__icontains=user_request) |
                 Q(genome__genome_id__icontains=user_request) | 
                 Q(genome__organism__icontains=user_request) ) |
                 Q(annotation__annotation_text__icontains=user_request)
            )

        if min_length:
            sequences = sequences.filter(sequence_length__gte=int(min_length))
        if max_length:
            sequences = sequences.filter(sequence_length__lte=int(max_length))
        if chromosome:
            sequences = sequences.filter(information_support__iexact=chromosome)
        if Brin:
            sequences = sequences.filter(sequence_brin__iexact=Brin)
        if sequence_type:
            sequences = sequences.filter(selected_type_iexact=sequence_type)
        if is_annotated:
                sequences = sequences.filter(
                    Q(sequence_status__iexact="Validated") | Q(sequence_status__iexact="Awaiting validation")
                            )


    # 2- Récupérer les champs sélectionnés
    selected_fields = request.GET

    fields = []

    if selected_type == "genome":
        if selected_fields.get("genome_id"):
            fields.append("genome_id")
        if selected_fields.get("genome_sequence"):
            fields.append("genome_sequence")
        if selected_fields.get("genome_type"):
            fields.append("genome_type")
        if selected_fields.get("genome_organisme"):
            fields.append("organism")
        if selected_fields.get("genome_annotation"):
            fields.append("is_annotated")
    else:  # Si c'est une séquence

        if selected_fields.get("sequence_id"):
            fields.append("sequence_id")
        if selected_fields.get("genome"):
            fields.append("genome")
        if selected_fields.get("organisme"):
            fields.append("organism")

        if selected_fields.get("dna_sequence"):
            fields.append("dna_sequence")
        if selected_fields.get("aa_sequence"):
            fields.append("aa_sequence")

        if selected_fields.get("sequence_start"):
            fields.append("sequence_start")
        if selected_fields.get("sequence_stop"):
            fields.append("sequence_stop")
        if selected_fields.get("sequence_length"):
            fields.append("sequence_length")
        if selected_fields.get("Brin_champ"):
            fields.append("sequence_brin")
        if selected_fields.get("support"):
            fields.append("information_support")

        if selected_fields.get("sequence_name"):
            fields.append("gene_name")
        if selected_fields.get("sequence_pep"):
            fields.append("peptide_product")
        if selected_fields.get("sequence_annot"):
            fields.append("annotation_text")
        if selected_fields.get("sequence_annot_status"):
            fields.append("sequence_status")
        


    # 3 - Création du fichier CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="exported_results.csv"'

    writer = csv.writer(response, delimiter = ';')
    
    # Titre des colonnes selon les champs sélectionnés
    header = []

    if selected_type == "genome": 
        if "genome_id" in fields:
            header.append("Identifiant Génome")
        if "genome_sequence" in fields:
            header.append("Génome")
        if "genome_type" in fields:
            header.append("Type du Génome")
        if "organism" in fields:
            header.append("Organisme")
        if "is_annotated" in fields:
            header.append("Est entièrement annoté")
    else: 
        if "sequence_id" in fields:
            header.append("Identifiant de la séquence")
        if "genome" in fields:
            header.append("Identifiant du génome")
        if "organism" in fields:
            header.append("Espèce")

        if "dna_sequence" in fields:
            header.append("Séquence nucléotidique")
        if "aa_sequence" in fields:
            header.append("Séquence protéique")
        
        if "sequence_start" in fields:
            header.append("Position du premier nucléotide")
        if "sequence_stop" in fields:
            header.append("Position du dernier nucléotide")
        if "sequence_length" in fields:
            header.append("Taille")
        if "sequence_brin" in fields:
            header.append("Brin")
        if "information_support" in fields:
            header.append("Support")

        if "gene_name" in fields:
            header.append("Nom du gène")
        if "peptide_product" in fields:
            header.append("Produit peptidique")
        if "annotation_text" in fields:
            header.append("Annotation")
        if "sequence_status" in fields:
            header.append("Statut de l'annotation")

    writer.writerow(header)

    # Remplir le CSV avec les données sélectionnées
    if selected_type == "genome":
        for genome in genomes:
            row = []
            if "genome_id" in fields:
                row.append(genome.genome_id)
            if "genome_sequence" in fields:
                row.append(genome.genome_sequence)
            if "genome_type" in fields:
                row.append(genome.genome_type)
            if "organism" in fields:
                row.append(genome.organism)
            if "is_annotated" in fields:
                row.append(genome.is_annotated)
            writer.writerow(row)

    if selected_type == "sequence":
        for sequence in sequences:
            row = []
            if "sequence_id" in fields:
                row.append(sequence.sequence_id)
            if "genome" in fields:
                row.append(sequence.genome.genome_id)
            if "organism" in fields:
                row.append(sequence.genome.organism)

            if "dna_sequence" in fields:
                row.append(sequence.dna_sequence)
            if "aa_sequence" in fields:
                row.append(sequence.aa_sequence)

            if "sequence_start" in fields:
                row.append(sequence.sequence_start)
            if "sequence_stop" in fields:
                row.append(sequence.sequence_stop)
            if "sequence_length" in fields:
                row.append(sequence.sequence_length)
            if "sequence_brin" in fields:
                row.append(sequence.sequence_brin)
            if "information_support" in fields:
                row.append(sequence.information_support)

            if "gene_name" in fields:
                row.append(sequence.gene_name)
            if "peptide_product" in fields:
                row.append(sequence.peptide_product)
            if "annotation_text" in fields:
                annotation_text = sequence.annotation.annotation_text if hasattr(sequence, 'annotation') else "NA"
                row.append(annotation_text)
            if "sequence_status" in fields:
                row.append(sequence.sequence_status)
            writer.writerow(row)

    print(f"🔹 Nombre de séquences trouvées: {sequences.count() if sequences else 0}")



    return response