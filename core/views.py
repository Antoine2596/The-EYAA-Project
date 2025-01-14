from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Page d'accueil
def home(request):
    return render(request,"core/home.html")

def contact(request):
    return render(request,"contacts/home.html")

def connexion(request):
    return render(request, "connexion.html")

# https://docs-djangoproject-com.translate.goog/en/5.1/topics/auth/default/?_x_tr_sl=en&_x_tr_tl=fr&_x_tr_hl=fr&_x_tr_pto=sc
@login_required
def profile(request):
    return render(request, "core/profile.html")