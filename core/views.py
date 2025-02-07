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


from django.http import HttpResponse
#from import_export.formats.base import BaseFormat
from .resources import GenomeResource
from .admin import GenomeImportForm

# Page d'accueil
def page_non_connecte(request):
    return render(request, "core/non_connecte.html")

@login_required
def home(request):
    return render(request,"core/home.html")

# @login_required
# def home(request):
#     if request.user.role == "visiteur":
#         return HttpResponseForbidden("Vous êtes visiteurs : vous n’avez accès à rien.")
#     return render(request, "core/home.html") 


def contacts(request):
    return render(request,"core/contacts.html")

@login_required
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

    if request.method == 'POST':
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            return redirect('profile_informations')
    else:  
        password_form = PasswordChangeForm(user=request.user)

    return render(request, 'core/profile_change_PSWD.html', {
        'password_form': password_form})

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
    return redirect("page_non_connecte")


STATUS_COLORS = {
    "Nothing": "#FFB6C1",  # Rose clair
    "Assigned": "#ADD8E6",  # Bleu clair
    "Awaiting validation": "#FFD700",  # Jaune doré
    "Validated": "#90EE90",  # Vert clair
}

def highlight_sequences(genome_sequence, associated_sequences):
    highlighted = list(genome_sequence)  
    annotations = [] 

    for seq in associated_sequences:
        color = STATUS_COLORS.get(seq.sequence_status, "#D3D3D3")  
        url = f"/visualisation/sequence/{seq.sequence_id}"
        title = f"Gene: {seq.gene_name} ({seq.sequence_start}-{seq.sequence_stop}) - {seq.sequence_status}"

        start, stop = seq.sequence_start, seq.sequence_stop
        annotations.append((start, f'<a href="{url}" title="{title}" style="text-decoration: none; color: inherit;">'
                                   f'<mark style="background-color: {color};">'))
        annotations.append((stop, '</mark></a>'))

    for pos, tag in sorted(annotations, reverse=True):
        highlighted.insert(pos, tag)

    return "".join(highlighted) 


@login_required
def visualisation(request, obj_type, obj_id):
    if obj_type == "genome":
        obj = get_object_or_404(Genome, genome_id=obj_id)
        associated_sequences = obj.sequences.all()
        highlighted_sequence = highlight_sequences(
            obj.genome_sequence, associated_sequences
        )
    elif obj_type == "sequence":
        obj = get_object_or_404(Sequence, sequence_id=obj_id)
        highlighted_sequence = None
    elif obj_type == "annotation":
        obj = get_object_or_404(Annotation, annotation_id=obj_id)
        highlighted_sequence = None
    else:
        return render(request, "core/404.html", {"message": "Type d'objet non reconnu."})

    return render(
        request,
        "core/visualisation.html",
        {
            "obj": obj,
            "obj_type": obj_type,
            "highlighted_sequence": highlighted_sequence,
        },
    )


def inscription(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = "visiteur"
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

def genome_list(request):
    genomes = Genome.objects.all()  # Récupère tous les génomes
    return render(request, "test.html", {"genomes": genomes})


def is_not_visitor(user):
    return user.role != "visiteur"

@login_required
@user_passes_test(is_not_visitor)
def database_view(request):
    user_request = request.GET.get("user_request", "").strip()
    filter_types = request.GET.getlist("filter_type")
    is_annotated = request.GET.get("is_annotated") == "true"
    min_length = request.GET.get("min_length")
    max_length = request.GET.get("max_length")
    chromosome = request.GET.get("chromosome", "").strip()

    genomes = sequences = annotations = None
    
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
        query = Q(genome_id__icontains=user_request) | Q(organism__icontains=user_request)
        if "genome" in filter_types or not filter_types:
            genomes = Genome.objects.filter(query)
            if is_annotated:
                genomes = genomes.filter(is_annotated=True)

        if "sequence" in filter_types or not filter_types:
            sequences = Sequence.objects.filter(
                Q(sequence_id__icontains=user_request) | Q(gene_name__icontains=user_request)
            )

            # Appliquer les filtres sur les résultats
            if min_length:
                sequences = sequences.filter(sequence_length__gte=int(min_length))
            if max_length:
                sequences = sequences.filter(sequence_length__lte=int(max_length))
            if chromosome:
                sequences = sequences.filter(num_chromosome__iexact=chromosome)

        if "annotation" in filter_types or not filter_types:
            annotations = Annotation.objects.filter(
                (Q(annotation_id__icontains=user_request) | Q(annotation_text__icontains=user_request)) &
                Q(is_validated=True))
        
        combined_results = [
            {"obj": obj, "type": "Genome"} for obj in genomes
        ] + [
            {"obj": obj, "type": "Sequence"} for obj in sequences
        ] + [
            {"obj": obj, "type": "Annotation"} for obj in annotations
        ]
        
        # Pagination
        paginator = Paginator(combined_results, 3)  # 10 résultats par page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            "dashboard": False,
            "page_obj": page_obj,
            "total_genomes": len(genomes),
            "total_sequences": len(sequences),
            "total_annotations": len(annotations),
        }

    return render(request, "core/database.html", context)

# Vérifier que l'utilisateur est un validateur
def is_validator(user):
    return user.role == "validateur"


@user_passes_test(is_validator)
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
    annotateurs = CustomUser.objects.filter(role__in=["annotateur", "validateur"])
    
    if request.method == "POST":
        annotateur_id = request.POST.get("annotateur")
        annotateur = get_object_or_404(CustomUser, email = annotateur_id)

        Annotation.objects.create(
            annotation_id=f"ANN_{sequence_id}",
            annotation_text="",
            is_validated=False,
            annotation_author=annotateur,
            sequence=sequence_id,
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
