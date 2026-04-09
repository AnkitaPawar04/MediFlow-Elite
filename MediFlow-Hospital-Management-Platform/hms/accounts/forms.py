"""Forms for accounts app."""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class DoctorSignUpForm(UserCreationForm):
    """Form for doctor registration."""
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'new-password'
        }),
        required=True
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password'
        }),
        required=True
    )
    
    class Meta:
        """Meta options for DoctorSignUpForm."""
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
    
    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        email = cleaned_data.get('email', '').lower()
        
        # Check if email already exists
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email address is already registered. Please use a different email or login.")
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save user with doctor role."""
        user = super().save(commit=False)
        user.role = 'DOCTOR'
        user.email = user.email.lower()  # Normalize email to lowercase
        user.username = user.email
        if commit:
            user.save()
        return user


class PatientSignUpForm(UserCreationForm):
    """Form for patient registration."""
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    password1 = forms.CharField(
        label="Password", 
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'new-password'
        }),
        required=True
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password'
        }),
        required=True
    )
    
    class Meta:
        """Meta options for PatientSignUpForm."""
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
    
    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        email = cleaned_data.get('email', '').lower()
        
        # Check if email already exists
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email address is already registered. Please use a different email or login.")
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save user with patient role."""
        user = super().save(commit=False)
        user.role = 'PATIENT'
        user.email = user.email.lower()  # Normalize email to lowercase
        user.username = user.email
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form using email."""
    
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'autofocus': True}))
    password = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput)
    
    def __init__(self, request=None, *args, **kwargs):
        """Initialize form."""
        super().__init__(request, *args, **kwargs)
        # Remove username field and use email instead
        if 'username' in self.fields:
            del self.fields['username']
    
    def clean(self):
        """Clean and authenticate using email."""
        email = self.cleaned_data.get('email', '').lower().strip()
        password = self.cleaned_data.get('password')
        
        if email and password:
            try:
                # Try to get user by email (case-insensitive)
                user = CustomUser.objects.get(email__iexact=email)
                
                # Check password
                if not user.check_password(password):
                    self.add_error(None, "Invalid email or password. Please try again.")
                    return self.cleaned_data
                
                # Store user for get_user() method
                self.user_cache = user
                
            except CustomUser.DoesNotExist:
                self.add_error(None, "Invalid email or password. Please try again.")
        else:
            self.add_error(None, "Email and password are required.")
        
        return self.cleaned_data
    
    def get_user(self):
        """Return authenticated user."""
        return self.user_cache if hasattr(self, 'user_cache') else None
