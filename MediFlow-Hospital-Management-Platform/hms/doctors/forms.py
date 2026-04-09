"""Forms for doctors app."""
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime
from .models import AvailabilitySlot, MedicalHistory
from accounts.models import CustomUser


class AvailabilitySlotForm(forms.ModelForm):
    """Form for creating availability slots."""
    
    class Meta:
        """Meta options for AvailabilitySlotForm."""
        model = AvailabilitySlot
        fields = ('date', 'start_time', 'end_time')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def __init__(self, *args, doctor=None, **kwargs):
        """Initialize form with doctor instance for validation."""
        super().__init__(*args, **kwargs)
        self.doctor = doctor
    
    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if date and start_time and end_time:
            # Check if date is in future
            if date < timezone.now().date():
                raise ValidationError("Slot date must be in the future.")
            
            # Check if start time is before end time
            if start_time >= end_time:
                raise ValidationError("Start time must be before end time.")
            
            # Check for duplicate slot (same date, start_time, end_time for this doctor)
            if self.doctor:
                existing_slot = AvailabilitySlot.objects.filter(
                    doctor=self.doctor,
                    date=date,
                    start_time=start_time,
                    end_time=end_time
                ).exists()
                
                if existing_slot:
                    raise ValidationError(
                        f"You already have an availability slot on {date} from {start_time} to {end_time}. "
                        "Please choose a different time or date."
                    )
        
        return cleaned_data


class EditDoctorProfileForm(forms.ModelForm):
    """Form for editing doctor profile."""
    
    class Meta:
        """Meta options for EditDoctorProfileForm."""
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'username')
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username',
                'readonly': 'readonly'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].disabled = True


class UploadPatientReportForm(forms.ModelForm):
    """Form for uploading patient medical reports."""
    
    patient = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='PATIENT'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Select Patient'
    )
    
    class Meta:
        """Meta options for UploadPatientReportForm."""
        model = MedicalHistory
        fields = ('patient', 'condition', 'description', 'diagnosis_date', 'status', 'file_upload')
        widgets = {
            'condition': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Condition/Diagnosis'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Medical Details',
                'rows': 4
            }),
            'diagnosis_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'file_upload': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            }),
        }
    
    def __init__(self, doctor=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show patients that have booked this doctor
        if doctor:
            from bookings.models import Booking
            patient_ids = Booking.objects.filter(doctor=doctor).values_list('patient_id', flat=True).distinct()
            self.fields['patient'].queryset = CustomUser.objects.filter(id__in=patient_ids, role='PATIENT')

