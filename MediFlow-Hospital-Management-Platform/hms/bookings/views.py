"""Views for bookings app."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from doctors.models import AvailabilitySlot
from .models import Booking
from services.email_client import send_booking_confirmation, send_booking_cancelled
from services.google_calendar import create_calendar_event


@login_required(login_url='login')
@require_http_methods(["POST"])
def book_appointment(request, slot_id):
    """Book an appointment - with transaction and locking to prevent race conditions."""
    
    if not request.user.is_patient():
        messages.error(request, "Only patients can book appointments.")
        return redirect('login')
    
    # Check if patient already has a booking
    if Booking.objects.filter(patient=request.user).exists():
        messages.error(request, "You already have a booking. Cancel it first to book another.")
        return redirect('patient_dashboard')
    
    try:
        with transaction.atomic():
            # Use select_for_update() to lock the slot
            slot = AvailabilitySlot.objects.select_for_update().get(id=slot_id)
            
            # Double-check if slot is available
            if slot.is_booked or not slot.can_be_booked():
                messages.error(request, "This slot is no longer available.")
                return redirect('view_slots')
            
            # Create booking
            booking = Booking.objects.create(
                patient=request.user,
                doctor=slot.doctor,
                slot=slot
            )
            
            # Mark slot as booked
            slot.is_booked = True
            slot.save()
            
            # Send email notification
            try:
                send_booking_confirmation(booking)
            except Exception as e:
                # Log error but don't fail the booking
                print(f"Error sending email: {str(e)}")
            
            # Create Google Calendar events for both doctor and patient
            try:
                create_calendar_event(slot.doctor, booking)
                create_calendar_event(request.user, booking)
            except Exception as e:
                # Log error but don't fail the booking
                print(f"Error creating calendar event: {str(e)}")
            
            messages.success(request, "Appointment booked successfully!")
            return redirect('patient_dashboard')
    
    except AvailabilitySlot.DoesNotExist:
        messages.error(request, "Slot not found.")
        return redirect('view_slots')
    except Exception as e:
        messages.error(request, f"Error booking appointment: {str(e)}")
        return redirect('view_slots')


@login_required(login_url='login')
@require_http_methods(["POST"])
def cancel_booking(request):
    """Cancel a booking."""
    
    if not request.user.is_patient():
        messages.error(request, "Only patients can cancel bookings.")
        return redirect('login')
    
    try:
        with transaction.atomic():
            booking = Booking.objects.select_related('slot').get(patient=request.user)
            
            # Send cancellation email before deleting
            try:
                send_booking_cancelled(booking)
            except Exception as e:
                pass
            
            # Mark slot as available
            slot = booking.slot
            slot.is_booked = False
            slot.save()
            
            # Delete booking
            booking.delete()
            
            messages.success(request, "Booking cancelled successfully.")
            return redirect('patient_dashboard')
    
    except Booking.DoesNotExist:
        messages.error(request, "No booking found.")
        return redirect('patient_dashboard')
    except Exception as e:
        messages.error(request, f"Error cancelling booking: {str(e)}")
        return redirect('patient_dashboard')
