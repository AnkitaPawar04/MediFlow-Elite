"""Patients app configuration."""
from django.apps import AppConfig


class PatientsConfig(AppConfig):
    """Configuration for patients app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'patients'
