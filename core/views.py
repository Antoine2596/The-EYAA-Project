from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .form import CustomUserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Page d'accueil
def home(request):
    return render(request,"core/home.html")

# Contacts
def contact(request):
    return render(request,"core/contacts.html")

def database(request):
    return render(request, "core/database.html")

def visualisation(request):
    return render(request, "core/visualisation.html")

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