from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("inscription/", views.inscription, name="inscription"),
    path("connexion/", views.connexion, name="connexion"),
    path("contacts/", views.contacts, name="contacts"),
    path("database/", views.database_view, name="genome_database"),
    path("visualisation/<str:obj_type>/<str:obj_id>/", views.visualisation, name="visualisation"),
]