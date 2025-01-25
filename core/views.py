from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from .form_inscription import CustomUserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Genome, Sequence, Annotation, ConnexionHistorique
from django.db.models import Q
from django.contrib.auth import logout
from django.utils.timezone import now

# Page d'accueil
def home(request):
    return render(request,"core/home.html")

# Contacts
def contacts(request):
    return render(request,"core/contacts.html")

@login_required
def profile(request):
    return render(request, "core/profile.html")
    
def Pageinscription(request):
    return render(request, "core/inscription.html")

def database(request):
    return render(request, "core/database.html")

# https://docs.djangoproject.com/fr/5.1/topics/auth/default/
# deconnexion
def deconnexion(request):
    logout(request)
    return redirect("home")

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


def connexion(request):
    if request.method == "POST":

        email = request.POST.get("email", "")
        password = request.POST.get("password", "") 


        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Connexion réussie !")
            return redirect("home")
        else:
            messages.error(request, "Adresse email ou mot de passe incorrect.")
    return render(request, "core/connexion.html")


def inscription(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('connexion')
    else:
        form = CustomUserCreationForm()
        
    return render(request, "core/inscription.html", {"form": form})

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

def get_client_ip(request):
    """Récupérer l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def connexion(request):
    if request.method == "POST":
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Connexion réussie !")

            # Enregistrer l'historique de connexion
            ConnexionHistorique.objects.create(
                user=user,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                timestamp=now()
            )

            return redirect("home")
        else:
            messages.error(request, "Adresse email ou mot de passe incorrect.")

    return render(request, "core/connexion.html")