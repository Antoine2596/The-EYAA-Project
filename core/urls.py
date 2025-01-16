from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('genome_viewer/', views.genome_viewer, name='genome_viewer'),
]