"""Views for doctors app."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import AvailabilitySlot
from .forms import AvailabilitySlotForm
from bookings.models import Booking


def doctor_only(view_func):
    """Decorator to check if user is a doctor."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_doctor():
            messages.error(request, "You don't have permission to access this page.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required(login_url='login')
@doctor_only
def doctor_dashboard(request):
    """Doctor dashboard view."""
    doctor = request.user
    slots = AvailabilitySlot.objects.filter(doctor=doctor).order_by('-date', 'start_time')
    bookings = Booking.objects.filter(doctor=doctor).select_related('patient').order_by('-created_at')
    
    context = {
        'slots_count': slots.count(),
        'booked_slots_count': slots.filter(is_booked=True).count(),
        'available_slots_count': slots.filter(is_booked=False).count(),
        'total_bookings': bookings.count(),
        'recent_bookings': bookings[:5],
        'slots': slots[:10],
    }
    
    return render(request, 'doctors/dashboard.html', context)


@login_required(login_url='login')
@doctor_only
@require_http_methods(["GET", "POST"])
def create_availability(request):
    """Create availability slot."""
    if request.method == 'POST':
        form = AvailabilitySlotForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.doctor = request.user
            slot.save()
            messages.success(request, "Availability slot created successfully.")
            return redirect('doctor_dashboard')
    else:
        form = AvailabilitySlotForm()
    
    return render(request, 'doctors/create_availability.html', {'form': form})


@login_required(login_url='login')
@doctor_only
def manage_availability(request):
    """Manage availability slots."""
    slots = AvailabilitySlot.objects.filter(doctor=request.user).order_by('-date', 'start_time')
    
    context = {
        'slots': slots,
    }
    
    return render(request, 'doctors/manage_availability.html', context)


@login_required(login_url='login')
@doctor_only
@require_http_methods(["POST"])
def delete_availability(request, slot_id):
    """Delete availability slot."""
    slot = get_object_or_404(AvailabilitySlot, id=slot_id, doctor=request.user)
    
    if slot.is_booked:
        messages.error(request, "Cannot delete a booked slot.")
        return redirect('manage_availability')
    
    slot.delete()
    messages.success(request, "Availability slot deleted successfully.")
    return redirect('manage_availability')


@login_required(login_url='login')
@doctor_only
def view_bookings(request):
    """View doctor's bookings."""
    bookings = Booking.objects.filter(doctor=request.user).select_related(
        'patient', 'slot'
    ).order_by('-created_at')
    
    context = {
        'bookings': bookings,
    }
    
    return render(request, 'doctors/view_bookings.html', context)
