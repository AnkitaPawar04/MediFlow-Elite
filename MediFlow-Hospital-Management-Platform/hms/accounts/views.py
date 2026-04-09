"""Views for accounts app."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.contrib import messages
import os
import random
import string
from .forms import DoctorSignUpForm, PatientSignUpForm, CustomAuthenticationForm
from services.google_calendar import get_google_auth_url, handle_oauth_callback
from services.email_client import send_signup_welcome, send_password_reset_otp
from accounts.models import CustomUser, PasswordResetOTP


@ensure_csrf_cookie
def home(request):
    """Home page - show landing page or redirect based on authentication."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')


def index(request):
    """Index page - same as home."""
    return home(request)


@require_http_methods(["GET", "POST"])
@csrf_protect
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
            return redirect('home')
    else:
        form = DoctorSignUpForm()
    
    return render(request, 'accounts/doctor_signup.html', {'form': form})


@require_http_methods(["GET", "POST"])
@csrf_protect
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
            return redirect('home')
    else:
        form = PatientSignUpForm()
    
    return render(request, 'accounts/patient_signup.html', {'form': form})



@require_http_methods(["GET", "POST"])
@ensure_csrf_cookie
@csrf_protect
def login_view(request):
    """Handle user login with role-based redirection."""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        # Get the role that user was trying to login as
        role = request.POST.get('role', 'admin')
        
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)
                # Redirect based on user role
                if user.is_staff or user.is_superuser:
                    return redirect('admin_management:dashboard')
                elif user.is_doctor():
                    return redirect('doctor_dashboard')
                else:
                    return redirect('patient_dashboard')
            else:
                messages.error(request, "Authentication failed. Please try again.")
        else:
            # Form is invalid, messages are already added by the form
            pass
        
        # Redirect back to home with tab parameter
        return redirect(f'/?tab={role}')
    
    # GET request - redirect to home
    return redirect('home')


@require_http_methods(["GET", "POST"])
def forgot_password(request):
    """Handle forgot password - send OTP to email."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()  # Normalize to lowercase
        
        try:
            user = CustomUser.objects.get(email=email)
            
            # Generate 6-digit OTP
            otp = ''.join(random.choices(string.digits, k=6))
            
            # Save or update OTP in database
            password_reset_otp, created = PasswordResetOTP.objects.update_or_create(
                user=user,
                defaults={'otp': otp, 'is_verified': False}
            )
            
            # Send OTP via email
            try:
                send_password_reset_otp(user, otp)
                messages.success(request, f"OTP has been sent to {email}")
                return redirect('reset_password')
            except Exception as e:
                error_msg = str(e)
                # Show detailed error in development mode
                if 'logged to console' in error_msg or 'not configured' in error_msg or 'unavailable' in error_msg:
                    messages.warning(request, f"⚠️  {error_msg}")
                    # Still allow proceeding to reset password entry for development
                    messages.info(request, f"📧 Your OTP is logged in the server console. Please check the terminal output.")
                    return redirect('reset_password')
                else:
                    messages.error(request, "Failed to send OTP. Please try again.")
                return render(request, 'accounts/forgot_password.html')
        
        except CustomUser.DoesNotExist:
            # Don't reveal if email exists or not for security
            messages.success(request, f"If {email} exists, an OTP has been sent")
            return redirect('reset_password')
    
    return render(request, 'accounts/forgot_password.html')


@require_http_methods(["GET", "POST"])
def reset_password(request):
    """Handle password reset with OTP verification."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        otp = request.POST.get('otp', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        email = request.POST.get('email', '').strip().lower()  # Normalize to lowercase
        
        # Validate password match
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'accounts/reset_password.html', {'email': email})
        
        # Validate password length
        if len(new_password) < 8:
            messages.error(request, "Password must be at least 8 characters")
            return render(request, 'accounts/reset_password.html', {'email': email})
        
        try:
            user = CustomUser.objects.get(email=email)
            
            # Get OTP record
            otp_record = PasswordResetOTP.objects.get(user=user)
            
            # Verify OTP
            if otp_record.is_expired():
                messages.error(request, "OTP has expired. Please request a new one")
                return redirect('forgot_password')
            
            if otp_record.otp != otp:
                messages.error(request, "Invalid OTP")
                return render(request, 'accounts/reset_password.html', {'email': email})
            
            # Reset password
            user.set_password(new_password)
            user.save()
            
            # Mark OTP as used
            otp_record.delete()
            
            messages.success(request, "Password reset successfully! You can now login with your new password")
            return redirect('home')
        
        except CustomUser.DoesNotExist:
            messages.error(request, "User not found")
            return redirect('forgot_password')
        except PasswordResetOTP.DoesNotExist:
            messages.error(request, "Please request an OTP first")
            return redirect('forgot_password')
    
    return render(request, 'accounts/reset_password.html')
@require_http_methods(["POST"])
def logout_view(request):
    """Handle user logout."""
    logout(request)
    return redirect('home')


def csrf_failure_view(request, reason=""):
    """Custom CSRF failure handler."""
    context = {
        'reason': reason,
        'title': 'CSRF Verification Failed',
        'message': 'The page you are trying to access has expired. Please refresh the page and try again.',
    }
    return render(request, 'csrf_error.html', context, status=403)


@login_required(login_url='home')
def dashboard(request):
    """Route to appropriate dashboard based on user role."""
    if request.user.is_doctor():
        return redirect('doctor_dashboard')
    else:
        return redirect('patient_dashboard')


@login_required(login_url='home')
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
        return redirect('home')

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
        return redirect('home')