"""URLs for accounts app."""
from django.urls import path
from . import views

urlpatterns = [
    path('signup/doctor/', views.doctor_signup, name='doctor_signup'),
    path('signup/patient/', views.patient_signup, name='patient_signup'),
    path('login/', views.login_view, name='login'),  # Internal endpoint for landing page form submission
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
]
