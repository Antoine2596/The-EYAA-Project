from django.shortcuts import render

# Page d'accueil
def home(request):
    return render(request,"core/home.html")

def contact(request):
    return render(request,"contacts/home.html")

def connexion(request):
    return render(request, "connexion.html")