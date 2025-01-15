from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("inscription/", views.inscription, name="inscription"),
    path("connexion/", views.connexion, name="connexion"),
    path("contacts/", views.contact, name="contacts"),
    path("visualisation/", views.visualisation, name = "visualisation"),
    path("database/", views.database, name="genome_database")
]