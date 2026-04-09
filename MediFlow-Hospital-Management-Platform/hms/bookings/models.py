"""Models for bookings app."""
from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import CustomUser
from doctors.models import AvailabilitySlot


class Booking(models.Model):
    """Model for booking appointments."""
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    patient = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='bookings',
        limit_choices_to={'role': 'PATIENT'}
    )
    
    doctor = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='patient_bookings',
        limit_choices_to={'role': 'DOCTOR'}
    )
    
    slot = models.OneToOneField(
        AvailabilitySlot,
        on_delete=models.CASCADE,
        related_name='booking'
    )
    
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        help_text="Payment status for the consultation"
    )
    payment_id = models.CharField(max_length=100, blank=True, null=True, help_text="Razorpay payment ID")
    
    created_at = models.DateTimeField(auto_now_add=True)
    reminder_sent_24h = models.BooleanField(default=False, help_text="Whether 24-hour reminder has been sent")
    reminder_sent_1h = models.BooleanField(default=False, help_text="Whether 1-hour reminder has been sent")
    
    class Meta:
        """Meta options for Booking."""
        db_table = 'bookings_booking'
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-created_at']
    
    def __str__(self):
        """String representation."""
        return f"Booking: {self.patient.email} with {self.doctor.email} on {self.slot.date}"
    
    def clean(self):
        """Validate booking."""
        if not self.slot.can_be_booked():
            raise ValidationError("This slot cannot be booked.")
    
    def is_paid(self):
        """Check if booking is paid."""
        return self.payment_status == 'completed'
