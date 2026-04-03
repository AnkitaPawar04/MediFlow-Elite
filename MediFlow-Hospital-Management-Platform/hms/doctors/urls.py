"""URLs for doctors app."""
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('create-availability/', views.create_availability, name='create_availability'),
    path('manage-availability/', views.manage_availability, name='manage_availability'),
    path('delete-availability/<int:slot_id>/', views.delete_availability, name='delete_availability'),
    path('bookings/', views.view_bookings, name='doctor_view_bookings'),
]
