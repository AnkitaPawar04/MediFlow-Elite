"""Forms for accounts app."""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class DoctorSignUpForm(UserCreationForm):
    """Form for doctor registration."""
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    
    class Meta:
        """Meta options for DoctorSignUpForm."""
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
    
    def save(self, commit=True):
        """Save user with doctor role."""
        user = super().save(commit=False)
        user.role = 'DOCTOR'
        user.username = user.email
        if commit:
            user.save()
        return user


class PatientSignUpForm(UserCreationForm):
    """Form for patient registration."""
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    
    class Meta:
        """Meta options for PatientSignUpForm."""
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
    
    def save(self, commit=True):
        """Save user with patient role."""
        user = super().save(commit=False)
        user.role = 'PATIENT'
        user.username = user.email
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form."""
    
    username = forms.EmailField(label="Email")
    
    def __init__(self, *args, **kwargs):
        """Initialize form."""
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None
