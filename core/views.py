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


# Page d'accueil
def home(request):
    return render(request,"core/home.html")


def contacts(request):
    return render(request,"core/contacts.html")

@login_required
def profile(request):
    return render(request, "core/base_profile.html")

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

    if status_filter == "validated":
        annotations = annotations.filter(is_validated=True)
    elif status_filter == "awaiting":
        annotations = annotations.filter(is_validated=False, sequence__sequence_status = "Awaiting validation")
    elif status_filter == "assigned":
        annotations = annotations.filter(is_validated=False, sequence__sequence_status = "Assigned")

    annotations_count = annotations.count()

    return render(request, 'core/profile_annotations.html', {'annotations': annotations,'status_filter': status_filter,
        'annotations_count': annotations_count})


def Pageinscription(request):
    return render(request, "core/inscription.html")

def database(request):
    return render(request, "core/database.html")

def deconnexion(request):
    logout(request)
    return redirect("home")

def visualisation(request, obj_type, obj_id):
    if obj_type == "genome":
        obj = get_object_or_404(Genome, genome_id=obj_id)
    elif obj_type == "sequence":
        obj = get_object_or_404(Sequence, sequence_id = obj_id)
    elif obj_type == "annotation":
        obj = get_object_or_404(Annotation, annotation_id=obj_id)
    else:
        return render(request, "core/404.html", {"message": "Type d'objet non reconnu."})

    return render(request, "core/visualisation.html", {"obj": obj, "obj_type": obj_type})


def inscription(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
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


def database_view(request):
    user_request = request.GET.get("user_request", "").strip()
    filter_types = request.GET.getlist("filter_type")
    is_annotated = request.GET.get("is_annotated") == "true"
    min_length = request.GET.get("min_length")
    max_length = request.GET.get("max_length")
    chromosome = request.GET.get("chromosome", "").strip()

    genomes = sequences = annotations = None

    # Recherche filtrée
    if user_request:
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
    else:
        # Pas de recherche, afficher tout
        if "genome" in filter_types or not filter_types:
            genomes = Genome.objects.all()
            if is_annotated:
                genomes = genomes.filter(is_annotated=True)
        if "sequence" in filter_types or not filter_types:
            sequences = Sequence.objects.all()

            # Appliquer les filtres sur les résultats
            if min_length:
                sequences = sequences.filter(sequence_length__gte=int(min_length))
            if max_length:
                sequences = sequences.filter(sequence_length__lte=int(max_length))
            if chromosome:
                sequences = sequences.filter(num_chromosome__iexact=chromosome)

        if "annotation" in filter_types or not filter_types:
            annotations = Annotation.objects.filter(Q(is_validated=True))

    return render(request, "core/database.html", {
        "genomes": genomes,
        "sequences": sequences,
        "annotations": annotations,
    })

# Vérifier que l'utilisateur est un validateur
def is_validator(user):
    return user.role == "validateur"

@user_passes_test(is_validator)
def annotations_listing(request):
    non_validated_annotations = Annotation.objects.filter(sequence__sequence_status="Awaiting validation")

    return render(request, "core/annotations_non_validates.html", {"annotations": non_validated_annotations})

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
            
        elif action == "reject":
            annotation.is_validated = False
            annotation.rejected_comment = comment
            sequence.sequence_status = "Assigned"

        annotation.save()
        sequence.save()
    
        return redirect("annotations_listing")
    
    return render(request, "core/validation_annotation.html", {"annotation": annotation, "user": request.user})

@user_passes_test(is_validator)
def sequences_non_assigned(request):
    non_assigned_sequence = Sequence.objects.filter(sequence_status="Nothing")
    return render(request, "core/sequences_non_assigned.html", {"sequences": non_assigned_sequence})

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
            is_validated=False
        )

        sequence_id.sequence_status = "Assigned"
        sequence_id.save()

        messages.success(request,  f"La séquence {sequence_id} a été attribuée à {annotateur.email}.")
        return redirect("sequences_non_assigned")

    return render(request, "core/attribution_sequence.html", {"sequence": sequence_id, "annotateurs": annotateurs})

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