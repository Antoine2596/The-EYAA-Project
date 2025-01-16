from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from .form import CustomUserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Genome

# Page d'accueil
def home(request):
    return render(request,"core/home.html")

# Contacts
def contacts(request):
    return render(request,"core/contacts.html")

def database(request):
    return render(request, "core/database.html")

def visualisation(request, genome_id):
    genome = get_object_or_404(Genome, genome_id=genome_id)

    return render(request, "core/visualisation.html", {"genome": genome})

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
    user_request = request.GET.get("user_request", "")
    sequence_type = request.GET.get("sequence_type", "")

    if not user_request and not sequence_type:
        results = Genome.objects.all()
    else:
        results = Genome.objects.filter(
            organism__icontains=user_request,
            genome_type__icontains=sequence_type
        )

    context = {"results": results}
    return render(request,"core/database.html", context)

# def database_search(request):
#     query = request.GET.get("user_request", "")
#     seq_type = request.GET.get("sequence_type", "")

#     listing_of_results = Genome.objects.all()

#     if query:
#         listing_of_results = listing_of_results.filter(
#             organism__icontains=query) | listing_of_results.filter(
#                 sequence_id__icontains=query) | listing_of_results.filter(genome_organism_icontains=query)
#     if seq_type:
#         if seq_type == "DNA" or seq_type == "RNA":
#             listing_of_results = listing_of_results.filter(genome__genome_type=seq_type)
    
#     return render(request, "database.html", {"sequences": listing_of_results})