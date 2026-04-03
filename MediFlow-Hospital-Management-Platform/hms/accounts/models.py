"""Custom user model for HMS."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom user model extending AbstractUser."""
    
    ROLE_CHOICES = (
        ('DOCTOR', 'Doctor'),
        ('PATIENT', 'Patient'),
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='PATIENT'
    )
    
    google_calendar_token = models.JSONField(
        null=True,
        blank=True,
        help_text="OAuth token for Google Calendar"
    )
    
    class Meta:
        """Meta options for CustomUser."""
        db_table = 'accounts_customuser'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        """String representation."""
        return f"{self.email} ({self.get_role_display()})"
    
    def is_doctor(self):
        """Check if user is a doctor."""
        return self.role == 'DOCTOR'
    
    def is_patient(self):
        """Check if user is a patient."""
        return self.role == 'PATIENT'
