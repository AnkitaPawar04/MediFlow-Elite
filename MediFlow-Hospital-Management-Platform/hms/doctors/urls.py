"""URLs for doctors app."""
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard & Overview
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    
    # Appointment Management
    path('appointments/', views.appointments_management, name='appointments_management'),
    path('appointment/<int:booking_id>/note/', views.add_consultation_note, name='add_consultation_note'),
    
    # Availability Management
    path('create-availability/', views.create_availability, name='create_availability'),
    path('manage-availability/', views.manage_availability, name='manage_availability'),
    path('delete-availability/<int:slot_id>/', views.delete_availability, name='delete_availability'),
    path('bookings/', views.view_bookings, name='doctor_view_bookings'),
    
    # Profile Management
    path('edit-profile/', views.edit_doctor_profile, name='edit_doctor_profile'),
    
    # Report Management
    path('upload-report/', views.upload_patient_report, name='upload_patient_report'),
    
    # Prescription Management
    path('prescriptions/', views.prescription_management, name='prescription_management'),
    path('prescription/create/', views.create_prescription, name='create_prescription'),
    
    # Patient Records
    path('medical-history/', views.patient_medical_history, name='patient_medical_history'),
    path('medical-history/<int:patient_id>/add/', views.add_medical_history, name='add_medical_history'),
    
    # Earnings & Payments
    path('earnings/', views.earnings_dashboard, name='earnings_dashboard'),
    
    # Ratings & Reviews
    path('ratings/', views.doctor_ratings, name='doctor_ratings'),
    path('ratings/<int:rating_id>/reply/', views.reply_to_review, name='reply_to_review'),
]
