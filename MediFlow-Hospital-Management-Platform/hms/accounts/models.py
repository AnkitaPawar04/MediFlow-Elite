"""Custom user model for HMS."""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


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
    
    is_2fa_enabled = models.BooleanField(
        default=False,
        help_text="Whether two-factor authentication is enabled"
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


class PasswordResetOTP(models.Model):
    """Model to store OTP for password reset."""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='password_reset_otp')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'accounts_password_reset_otp'
    
    def __str__(self):
        return f"OTP for {self.user.email}"
    
    def is_expired(self):
        """Check if OTP has expired (valid for 10 minutes)."""
        return timezone.now() > self.created_at + timedelta(minutes=10)
