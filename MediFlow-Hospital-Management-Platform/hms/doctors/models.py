"""Models for doctors app."""
from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from django.core.validators import MinValueValidator, MaxValueValidator


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
    is_recurring = models.BooleanField(default=False, help_text="Repeat every week on this day")
    max_patients_per_day = models.IntegerField(default=10)
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


class ConsultationNote(models.Model):
    """Model for doctor consultation notes after appointments."""
    
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='consultation_notes')
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='patient_notes')
    appointment_date = models.DateTimeField()
    notes = models.TextField()
    followup_required = models.BooleanField(default=False)
    followup_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctors_consultation_note'
        verbose_name = 'Consultation Note'
        verbose_name_plural = 'Consultation Notes'
        ordering = ['-appointment_date']
    
    def __str__(self):
        return f"{self.doctor.email} - {self.patient.email} ({self.appointment_date.date()})"


class Prescription(models.Model):
    """Model for prescriptions issued by doctors."""
    
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='prescriptions')
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='patient_prescriptions')
    medicines = models.JSONField(default=list, help_text="List of medicines with dosage and duration")
    instructions = models.TextField(blank=True)
    diagnosis = models.CharField(max_length=255)
    valid_until = models.DateField()
    digital_signature = models.CharField(max_length=255, blank=True)
    pdf_file = models.FileField(upload_to='prescriptions/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Prescription'
        verbose_name_plural = 'Prescriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Prescription: {self.patient.email} by {self.doctor.email}"


class Earning(models.Model):
    """Model for tracking doctor earnings."""
    
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='earnings')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    booking = models.ForeignKey('bookings.Booking', on_delete=models.SET_NULL, null=True, blank=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')],
        default='PENDING'
    )
    payment_date = models.DateField(null=True, blank=True)
    transaction_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Earning'
        verbose_name_plural = 'Earnings'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.doctor.email} - ₹{self.amount}"


class DoctorRating(models.Model):
    """Model for patient ratings and reviews of doctors."""
    
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ratings')
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='patient_ratings')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(blank=True)
    response = models.TextField(blank=True, help_text="Doctor's response to review")
    is_verified = models.BooleanField(default=True)  # Verified booking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Doctor Rating'
        verbose_name_plural = 'Doctor Ratings'
        ordering = ['-created_at']
        unique_together = ('doctor', 'patient')
    
    def __str__(self):
        return f"{self.doctor.email} - {self.rating}★ by {self.patient.email}"


class TelemedicineSession(models.Model):
    """Model for telemedicine/video consultation sessions."""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='telemedicine_sessions_doctor')
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='telemedicine_sessions_patient')
    booking = models.ForeignKey('bookings.Booking', on_delete=models.SET_NULL, null=True, blank=True)
    room_id = models.CharField(max_length=255, unique=True)  # Video call room identifier
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    scheduled_at = models.DateTimeField()
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=0)
    chat_transcript = models.TextField(blank=True)
    uploaded_documents = models.JSONField(default=list)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Telemedicine Session'
        verbose_name_plural = 'Telemedicine Sessions'
        ordering = ['-scheduled_at']
    
    def __str__(self):
        return f"Call: {self.doctor.email} ↔ {self.patient.email} on {self.scheduled_at.date()}"


class MedicalHistory(models.Model):
    """Model for storing patient medical history (maintained by doctor)."""
    
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='patient_records')
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='medical_history')
    condition = models.CharField(max_length=255)
    description = models.TextField()
    diagnosis_date = models.DateField()
    status_choices = [('active', 'Active'), ('resolved', 'Resolved'), ('chronic', 'Chronic')]
    status = models.CharField(max_length=20, choices=status_choices, default='active')
    file_upload = models.FileField(upload_to='medical_records/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Medical History'
        verbose_name_plural = 'Medical Histories'
        ordering = ['-diagnosis_date']
    
    def __str__(self):
        return f"{self.patient.email} - {self.condition}"
