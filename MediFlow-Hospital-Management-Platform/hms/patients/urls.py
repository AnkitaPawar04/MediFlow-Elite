"""URLs for patients app."""
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctors/', views.view_doctors, name='view_doctors'),
    path('slots/', views.view_available_slots, name='view_slots'),
    path('slots/<int:doctor_id>/', views.view_available_slots, name='view_doctor_slots'),
]
