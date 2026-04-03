"""Models for doctors app."""
from django.db import models
from django.utils import timezone
from accounts.models import CustomUser


class AvailabilitySlot(models.Model):
    """Model for doctor availability slots."""
    
    doctor = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='availability_slots',
        limit_choices_to={'role': 'DOCTOR'}
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Meta options for AvailabilitySlot."""
        db_table = 'doctors_availabilityslot'
        verbose_name = 'Availability Slot'
        verbose_name_plural = 'Availability Slots'
        ordering = ['-date', 'start_time']
        unique_together = ('doctor', 'date', 'start_time', 'end_time')
        indexes = [
            models.Index(fields=['doctor', 'date', 'is_booked']),
        ]
    
    def __str__(self):
        """String representation."""
        status = "Booked" if self.is_booked else "Available"
        return f"{self.doctor.email} - {self.date} {self.start_time}-{self.end_time} ({status})"
    
    def is_future_slot(self):
        """Check if slot is in the future."""
        from datetime import datetime
        slot_datetime = datetime.combine(self.date, self.start_time)
        return timezone.make_aware(slot_datetime) > timezone.now()
    
    def can_be_booked(self):
        """Check if slot can be booked."""
        return self.is_future_slot() and not self.is_booked
