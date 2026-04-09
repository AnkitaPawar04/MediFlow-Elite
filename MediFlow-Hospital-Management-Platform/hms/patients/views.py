"""Views for patients app."""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from doctors.models import AvailabilitySlot
from accounts.models import CustomUser
from bookings.models import Booking


def patient_only(view_func):
    """Decorator to check if user is a patient."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_patient():
            messages.error(request, "You don't have permission to access this page.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required(login_url='home')
@patient_only
@ensure_csrf_cookie
def patient_dashboard(request):
    """Patient dashboard view."""
    patient = request.user
    from django.utils import timezone
    
    # Get patient's booking
    booking = Booking.objects.filter(patient=patient).select_related(
        'doctor', 'slot'
    ).first()
    
    # Get statistics
    total_bookings = Booking.objects.filter(patient=patient).count()
    today = timezone.now().date()
    upcoming_count = Booking.objects.filter(
        patient=patient,
        slot__date__gte=today
    ).count()
    completed_count = Booking.objects.filter(
        patient=patient,
        slot__date__lt=today
    ).count()
    
    context = {
        'has_booking': booking is not None,
        'booking': booking,
        'total_bookings': total_bookings,
        'upcoming_count': upcoming_count,
        'completed_count': completed_count,
    }
    
    # Check if AJAX request
    if request.GET.get('ajax') == '1':
        return render(request, 'patients/dashboard_iframe.html', context)
    
    return render(request, 'patients/dashboard.html', context)


@login_required(login_url='home')
@patient_only
@ensure_csrf_cookie
def view_doctors(request):
    """View all doctors."""
    from django.db.models import Avg, Count
    from django.utils import timezone
    
    doctors = CustomUser.objects.filter(role='DOCTOR').order_by('first_name')
    
    # Enrich doctor data with ratings and availability slots
    doctors_data = []
    for doctor in doctors:
        # Get average rating
        avg_rating = doctor.ratings.aggregate(Avg('rating'))['rating__avg'] or 0
        rating_count = doctor.ratings.count()
        
        # Get available slots count
        available_slots = doctor.availability_slots.filter(
            is_booked=False,
            date__gte=timezone.now().date()
        ).count()
        
        doctors_data.append({
            'doctor': doctor,
            'avg_rating': round(avg_rating, 1) if avg_rating else 0,
            'rating_count': rating_count,
            'available_slots': available_slots,
        })
    
    context = {
        'doctors_data': doctors_data,
    }
    
    # AJAX request - return just the content without base layout
    if request.GET.get('ajax') == '1':
        return render(request, 'patients/doctors_iframe.html', context)
    
    return render(request, 'patients/view_doctors.html', context)


@login_required(login_url='home')
@patient_only
@ensure_csrf_cookie
def view_available_slots(request, doctor_id=None):
    """View available slots."""
    from django.utils import timezone
    from datetime import datetime
    
    # Get future available slots
    slots = AvailabilitySlot.objects.filter(
        is_booked=False,
        date__gte=timezone.now().date()
    ).select_related('doctor').order_by('date', 'start_time')
    
    if doctor_id:
        slots = slots.filter(doctor_id=doctor_id)
    
    context = {
        'slots': slots,
    }
    
    # AJAX request - return just the content without base layout
    if request.GET.get('ajax') == '1':
        return render(request, 'patients/slots_iframe.html', context)
    
    return render(request, 'patients/view_slots.html', context)


@login_required(login_url='home')
@patient_only
@ensure_csrf_cookie
def my_bookings(request):
    """View patient's all bookings."""
    from django.utils import timezone
    
    patient = request.user
    
    # Get all bookings for this patient
    bookings = Booking.objects.filter(patient=patient).select_related(
        'doctor', 'slot'
    ).order_by('-slot__date')
    
    context = {
        'bookings': bookings,
        'today': timezone.now().date(),
    }
    
    # AJAX request - return just the template content
    if request.GET.get('ajax') == '1':
        return render(request, 'patients/bookings_iframe.html', context)
    
    return render(request, 'patients/my_bookings.html', context)


@login_required(login_url='home')
@patient_only
@ensure_csrf_cookie
def patient_profile(request):
    """View/Edit patient profile."""
    patient = request.user
    
    context = {
        'patient': patient,
    }
    
    # AJAX request - return just the content without base layout
    if request.GET.get('ajax') == '1':
        return render(request, 'patients/profile_iframe.html', context)
    
    return render(request, 'patients/patient_profile.html', context)
