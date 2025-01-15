from django.shortcuts import render

# Page d'accueil
def home(request):
    return render(request,"core/home.html")
