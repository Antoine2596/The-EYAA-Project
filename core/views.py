from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from .form import CustomUserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Genome, Sequence, Annotation
from django.db.models import Q

# Page d'accueil
def home(request):
    return render(request,"core/home.html")

# Contacts
def contacts(request):
    return render(request,"core/contacts.html")

def database(request):
    return render(request, "core/database.html")

def visualisation(request, obj_type, obj_id):
    if obj_type == "genome":
        obj = get_object_or_404(Genome, genome_id=obj_id)
    elif obj_type == "sequence":
        obj = get_object_or_404(Sequence, sequence_id = obj_id)
    elif obj_type == "annoation":
        obj = get_object_or_404(Annotation, annotation_id=obj_id)
    else:
        return render(request, "core/404.html", {"message": "Type d'objet non reconnu."})

    return render(request, "core/visualisation.html", {"obj": obj, "obj_type": obj_type})


def inscription(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('connexion')  
    else:
        form = CustomUserCreationForm()  

    return render(request, 'core/inscription.html', {'form': form}) 

def connexion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")
    return render(request, 'core/connexion.html')


def genome_list(request):
    genomes = Genome.objects.all()  # Récupère tous les génomes
    return render(request, "test.html", {"genomes": genomes})


def database_view(request):
    user_request = request.GET.get("user_request", "").strip()
    filter_types = request.GET.getlist("filter_type")
    is_annotated = request.GET.get("is_annotated") == "true"

    # # Initialisation des résultats
    # genomes = sequences = annotations = None

    # # Recherche filtrée
    # if user_request:
    #     query = Q(genome_id__icontains=user_request) | Q(organism__icontains=user_request)
    #     if "genome" in filter_types or not filter_types:
    #         genomes = Genome.objects.filter(query)
    #         if is_annotated:
    #             genomes = genomes.filter(is_annotated=True)

    #     if "sequence" in filter_types or not filter_types:
    #         sequences = Sequence.objects.filter(
    #             Q(sequence_id__icontains=user_request) | Q(gene_name__icontains=user_request)
    #         )

    #     if "annotation" in filter_types or not filter_types:
    #         annotations = Annotation.objects.filter(
    #             Q(annotation_id__icontains=user_request) | Q(annotation_text__icontains=user_request)
    #         )
    # else:
    #     # Pas de recherche, afficher tout
    #     if "genome" in filter_types or not filter_types:
    #         genomes = Genome.objects.all()
    #         if is_annotated:
    #             genomes = genomes.filter(is_annotated=True)
    #     if "sequence" in filter_types or not filter_types:
    #         sequences = Sequence.objects.all()
    #     if "annotation" in filter_types or not filter_types:
    #         annotations = Annotation.objects.all()

    # return render(request, "core/database.html", {
    #     "genomes": genomes,
    #     "sequences": sequences,
    #     "annotations": annotations,
    # })

    min_length = request.GET.get("min_length")
    max_length = request.GET.get("max_length")
    chromosome = request.GET.get("chromosome", "").strip()
    sequence_type = request.GET.get("sequence_type", "").strip()

    # Initialisation des résultats
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

            # Appliquer les nouveaux filtres sur les séquences
            if min_length:
                sequences = sequences.filter(length__gte=int(min_length))
            if max_length:
                sequences = sequences.filter(length__lte=int(max_length))
            if chromosome:
                sequences = sequences.filter(chromosome__iexact=chromosome)
            if sequence_type:
                sequences = sequences.filter(type__iexact=sequence_type)

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

            # Appliquer les nouveaux filtres sur les séquences
            if min_length:
                sequences = sequences.filter(length__gte=int(min_length))
            if max_length:
                sequences = sequences.filter(length__lte=int(max_length))
            if chromosome:
                sequences = sequences.filter(chromosome__iexact=chromosome)
            if sequence_type:
                sequences = sequences.filter(type__iexact=sequence_type)

        if "annotation" in filter_types or not filter_types:
            annotations = Annotation.objects.all()

    return render(request, "core/database.html", {
        "genomes": genomes,
        "sequences": sequences,
        "annotations": annotations,
    })
