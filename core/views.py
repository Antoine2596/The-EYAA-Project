from django.shortcuts import render

from django.http import HttpResponse
#from import_export.formats.base import BaseFormat
from .resources import GenomeResource
from .admin import GenomeImportForm

# Page d'accueil
def home(request):
    return render(request,"core/home.html")

