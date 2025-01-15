from django.shortcuts import render
from django.http import HttpResponse

import re
from django.shortcuts import render, redirect
from django.contrib import messages
#from .forms import FastaUploadForm
from .models import Genome

# Create your views here.


def index(request):
    return HttpResponse("Page de test")

