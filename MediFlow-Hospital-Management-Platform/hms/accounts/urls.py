"""URLs for accounts app."""
from django.urls import path
from . import views

urlpatterns = [
    path('signup/doctor/', views.doctor_signup, name='doctor_signup'),
    path('signup/patient/', views.patient_signup, name='patient_signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('google/connect/', views.google_calendar_connect, name='google_calendar_connect'),
    
]
