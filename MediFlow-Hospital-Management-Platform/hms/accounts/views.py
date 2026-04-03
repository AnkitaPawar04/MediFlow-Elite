"""Views for accounts app."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
import os
from .forms import DoctorSignUpForm, PatientSignUpForm, CustomAuthenticationForm
from services.google_calendar import get_google_auth_url, handle_oauth_callback
from services.email_client import send_signup_welcome
from accounts.models import CustomUser


def home(request):
    """Home page - redirect based on authentication and role."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def index(request):
    """Index page - same as home."""
    return home(request)


@require_http_methods(["GET", "POST"])
def doctor_signup(request):
    """Handle doctor registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = DoctorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                send_signup_welcome(user)
            except Exception as e:
                pass
            login(request, user)
            return redirect('dashboard')
    else:
        form = DoctorSignUpForm()
    
    return render(request, 'accounts/doctor_signup.html', {'form': form})


@require_http_methods(["GET", "POST"])
def patient_signup(request):
    """Handle patient registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                send_signup_welcome(user)
            except Exception as e:
                pass
            login(request, user)
            return redirect('dashboard')
    else:
        form = PatientSignUpForm()
    
    return render(request, 'accounts/patient_signup.html', {'form': form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required(login_url='login')
@require_http_methods(["POST"])
def logout_view(request):
    """Handle user logout."""
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    """Route to appropriate dashboard based on user role."""
    if request.user.is_doctor():
        return redirect('doctor_dashboard')
    else:
        return redirect('patient_dashboard')


@login_required(login_url='login')
def google_calendar_connect(request):
    """Initiate Google Calendar OAuth flow."""
    try:
        if not os.path.exists('credentials.json'):
            messages.error(request, "Google credentials not configured. Please contact support.")
            return redirect('doctor_dashboard' if request.user.is_doctor() else 'patient_dashboard')
        
        auth_url, state = get_google_auth_url(request.user.id)
        request.session['google_oauth_state'] = state
        return redirect(auth_url)
    except Exception as e:
        messages.error(request, f"Error connecting to Google Calendar: {str(e)}")
        return redirect('doctor_dashboard' if request.user.is_doctor() else 'patient_dashboard')



def google_calendar_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')  # user.id

    if not code or not state:
        messages.error(request, "Google authentication failed.")
        return redirect('login')

    try:
        user = CustomUser.objects.get(id=state)

        # Restore session after OAuth redirect
        login(request, user)

        # Save Google Calendar token
        success = handle_oauth_callback(code, user)

        if success:
            messages.success(
                request,
                "Google Calendar connected successfully!"
            )
        else:
            messages.error(
                request,
                "Failed to connect Google Calendar."
            )

        # IMPORTANT: use `user`, NOT `request.user`
        if user.is_doctor():
            return redirect('doctor_dashboard')
        else:
            return redirect('patient_dashboard')

    except CustomUser.DoesNotExist:
        messages.error(request, "Invalid user session.")
        return redirect('login')