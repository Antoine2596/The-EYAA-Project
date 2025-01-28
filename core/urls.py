from django.urls import path
from . import views

urlpatterns = [
    path("", views.page_non_connecte, name="page_non_connecte"),
    path("home", views.home, name="home"),
    path("inscription/", views.inscription, name="inscription"),
    path("connexion/", views.connexion, name="connexion"),
    path("profile/", views.profile, name="profile"),
    path("contacts/", views.contacts, name="contacts"),
    path("database/", views.database_view, name="genome_database"),
    path("visualisation/<str:obj_type>/<str:obj_id>/", views.visualisation, name="visualisation"),
    path("deconnexion/", views.deconnexion, name="deconnexion"),
    path('profil/informations/', views.profile_informations, name='profile_informations'),
    path('profil/annotations/', views.profile_annotations, name='profile_annotations'),
]