from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("inscription/", views.inscription, name="inscription"),
    path("connexion/", views.connexion, name="connexion"),
    path("profile/", views.profile, name="profile"),
    path("contacts/", views.contacts, name="contacts"),
    path("database/", views.database_view, name="genome_database"),
    path("visualisation/<str:obj_type>/<str:obj_id>/", views.visualisation, name="visualisation"),
    path("deconnexion/", views.deconnexion, name="deconnexion"),
    path('profil/informations/', views.profile_informations, name='profile_informations'),
    path('profil/annotations/', views.profile_annotations, name='profile_annotations'),
    path("outil_validation/", views.annotations_listing, name="annotations_listing"),
    path("outil_validation/annotation_detail/<str:annotation_id>/", views.validate_annotation, name="validate_annotation"),
    path("attribution_sequence/", views.sequences_non_assigned, name="sequences_non_assigned"),
    path("attribution_sequence/sequence_detail/<str:sequence_id>/", views.attribution_sequence, name="attribution")
]