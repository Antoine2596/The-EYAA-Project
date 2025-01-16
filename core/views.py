from django.shortcuts import render

# Page d'accueil
def home(request):
    return render(request,"core/home.html")

def genome_viewer(request):
    return render(request, 'core/genome_viewer.html')