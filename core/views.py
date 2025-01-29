from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from .form_inscription import CustomUserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from .models import Genome, Sequence, Annotation
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.utils import timezone
from .models import ConnectionHistory

import re

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
    return render(request, 'core/profile_informations.html')

@login_required
def profile_annotations(request):
    if request.user.role == "lecteur":
        return HttpResponseForbidden("En tant que lecteur vous n'avez pas accès à cette fonctionnalité.")
    annotations = Annotation.objects.filter(annotation_author=request.user)
    return render(request, 'core/profile_annotations.html', {'annotations': annotations})

def Pageinscription(request):
    return render(request, "core/inscription.html")

def database(request):
    return render(request, "core/database.html")

def deconnexion(request):
    logout(request)
    return redirect("home")

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
                Q(annotation_id__icontains=user_request) | Q(annotation_text__icontains=user_request)
            )
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
            annotations = Annotation.objects.all()

    return render(request, "core/database.html", {
        "genomes": genomes,
        "sequences": sequences,
        "annotations": annotations,
    })

def deconnexion(request):
    if request.user.is_authenticated:
        last_conn = ConnectionHistory.objects.filter(
            user=request.user,
            logout_time__isnull=True
        ).order_by('-login_time').first()

        if last_conn:
            last_conn.logout_time = timezone.now()
            last_conn.save()

    logout(request)
    return redirect("home")




STATUS_COLORS = {
    "Nothing": "#FFB6C1",  # Rose clair
    "Assigned": "#ADD8E6",  # Bleu clair
    "Awaiting validation": "#FFD700",  # Jaune doré
    "Validated": "#90EE90",  # Vert clair
}


def highlight_sequences(genome_sequence, associated_sequences):
    highlighted = genome_sequence
    for seq in associated_sequences:
        color = STATUS_COLORS.get(seq.sequence_status, "#D3D3D3")  # Gris par défaut si inconnu
        pattern = re.escape(seq.dna_sequence)  
        url = f"/visualisation/sequence/{seq.sequence_id}"  
        title = f"Gene: {seq.gene_name} ({seq.sequence_start}-{seq.sequence_stop}) - {seq.sequence_status}"
        
        highlighted = re.sub(
            pattern,
            lambda match: (
                f'<a href="{url}" title="{title}"'
                f' style="text-decoration: none; color: inherit;">'
                f'<mark style="background-color: {color};">{match.group()}</mark>'
                f'</a>'
            ),
            highlighted,
        )
    return highlighted
