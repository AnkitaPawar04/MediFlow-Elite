"""Views for patients app."""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from doctors.models import AvailabilitySlot
from accounts.models import CustomUser
from bookings.models import Booking


def patient_only(view_func):
    """Decorator to check if user is a patient."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_patient():
            messages.error(request, "You don't have permission to access this page.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required(login_url='login')
@patient_only
def patient_dashboard(request):
    """Patient dashboard view."""
    patient = request.user
    
    # Get patient's booking
    booking = Booking.objects.filter(patient=patient).select_related(
        'doctor', 'slot'
    ).first()
    
    context = {
        'has_booking': booking is not None,
        'booking': booking,
    }
    
    return render(request, 'patients/dashboard.html', context)


@login_required(login_url='login')
@patient_only
def view_doctors(request):
    """View all doctors."""
    doctors = CustomUser.objects.filter(role='DOCTOR').order_by('first_name')
    
    context = {
        'doctors': doctors,
    }
    
    return render(request, 'patients/view_doctors.html', context)


@login_required(login_url='login')
@patient_only
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
    
    return render(request, 'patients/view_slots.html', context)
