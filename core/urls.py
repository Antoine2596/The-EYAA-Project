from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("profile/", views.profile, name="profile"),
    path("AnnotationPage/", views.AnnotationPage, name="AnnotationPage"),
    path("contacts/", views.contacts, name="contacts"),
    path("home/", views.home, name="home")
]