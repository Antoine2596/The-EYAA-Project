from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .forms import CustomUserCreationForm

def connexion(request):
    if request.method == "POST":
        # On récupère email et password du formulaire
        email = request.POST["email"]
        password = request.POST["password"]

        # On passe username=email, car USERNAME_FIELD = "email"
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Connexion réussie !")
            return redirect("home")
        else:
            messages.error(request, "Adresse email ou mot de passe incorrect.")
    return render(request, "connexion.html")


def inscription(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Compte créé avec succès. Vous pouvez maintenant vous connecter.")
            return redirect("connexion")
        else:
            messages.error(request, "Erreur lors de la création du compte.")
    else:
        form = CustomUserCreationForm()

    return render(request, "inscription.html", {"form": form})
