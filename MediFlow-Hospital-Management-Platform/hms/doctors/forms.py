"""Forms for doctors app."""
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime
from .models import AvailabilitySlot


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
        
        return cleaned_data
