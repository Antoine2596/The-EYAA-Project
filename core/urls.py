from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("inscription/", views.inscription, name="inscription"),
    path("connexion/", views.Pageconnexion, name="connexion"),
    path("contacts/", views.contacts, name="contacts"),
    path("database/", views.database_view, name="genome_database"),
    path("visualisation/<str:obj_type>/<str:obj_id>/", views.visualisation, name="visualisation"),
]