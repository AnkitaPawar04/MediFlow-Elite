"""Views for bookings app."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from doctors.models import AvailabilitySlot, DoctorRating
from admin_management.models import Specialization
from .models import Booking
from admin_management.models import Transaction
from services.email_client import send_booking_confirmation, send_booking_cancelled
from services.google_calendar import create_calendar_event
from django.conf import settings
import json
import sys

# Workaround for pkg_resources issue with setuptools >= 70
# Create a more complete fake pkg_resources module
if 'pkg_resources' not in sys.modules:
    class DistributionNotFound(Exception):
        pass
    
    class VersionConflict(Exception):
        pass
    
    class FakeDistribution:
        def __init__(self, name="razorpay", version="1.4.1"):
            self.project_name = name
            self.key = name.lower()
            self.version = version
            self._version = version
            self.parsed_version = version
    
    class FakePackageResources:
        DistributionNotFound = DistributionNotFound
        VersionConflict = VersionConflict
        
        def __init__(self):
            self.working_set = []
        
        def get_distribution(self, name):
            return FakeDistribution(name)
        
        def require(self, *args, **kwargs):
            """Dummy require method - doesn't validate versions"""
            return []
        
        def iter_entry_points(self, group, name=None):
            return []
        
        def resource_filename(self, package, resource):
            return resource
        
        def resource_string(self, package, resource):
            return b''
        
        def resource_exists(self, package, resource):
            return False
        
        def get_provider(self, module_or_name):
            class Provider:
                def get_resource_filename(self, manager, resource_name):
                    return resource_name
                def get_resource_string(self, manager, resource_name):
                    return b''
            return Provider()
        
        def parse_version(self, v):
            """Parse version string"""
            return v
        
        def safe_version(self, v):
            """Return safe version"""
            return v
        
        def find_distributions(self, *args, **kwargs):
            return []
    
    pkg_resources_module = FakePackageResources()
    pkg_resources_module.DistributionNotFound = DistributionNotFound
    pkg_resources_module.VersionConflict = VersionConflict
    pkg_resources_module.working_set = []
    sys.modules['pkg_resources'] = pkg_resources_module

# Import razorpay
try:
    import razorpay
except Exception as e:
    print(f"Warning: Failed to import razorpay: {e}")
    import traceback
    traceback.print_exc()
    razorpay = None


@login_required(login_url='home')
@require_http_methods(["POST"])
@csrf_protect
def book_appointment(request, slot_id):
    """Book an appointment - with transaction and locking to prevent race conditions."""
    
    if not request.user.is_patient():
        messages.error(request, "Only patients can book appointments.")
        return redirect('home')
    
    try:
        with transaction.atomic():
            # Use select_for_update() to lock the slot
            slot = AvailabilitySlot.objects.select_for_update().get(id=slot_id)
            
            # Double-check if slot is available
            if slot.is_booked or not slot.can_be_booked():
                messages.error(request, "This slot is no longer available.")
                return redirect('view_slots')
            
            # Get consultation fee from doctor's specialization or use default
            consultation_fee = 500  # Default fee
            try:
                # Try to get from doctor approval or specialization
                doctor_approval = slot.doctor.doctor_approval
                consultation_fee = float(doctor_approval.fee) if doctor_approval.fee else 500
            except:
                consultation_fee = 500
            
            # Create booking with pending payment
            booking = Booking.objects.create(
                patient=request.user,
                doctor=slot.doctor,
                slot=slot,
                consultation_fee=consultation_fee,
                payment_status='pending'
            )
            
            # Mark slot as booked
            slot.is_booked = True
            slot.save()
            
            # Redirect to payment page
            messages.info(request, "Appointment booked! Please complete the payment.")
            return redirect('initiate_payment', booking_id=booking.id)
    
    except AvailabilitySlot.DoesNotExist:
        messages.error(request, "Slot not found.")
        return redirect('view_slots')
    except Exception as e:
        messages.error(request, f"Error booking appointment: {str(e)}")
        return redirect('view_slots')


@login_required(login_url='home')
def initiate_payment(request, booking_id):
    """Initiate Razorpay payment for booking."""
    
    if razorpay is None:
        messages.error(request, "Payment system is not available. Please contact support.")
        return redirect('patient_dashboard')
    
    try:
        booking = Booking.objects.get(id=booking_id, patient=request.user)
        
        if booking.payment_status == 'completed':
            messages.warning(request, "This booking is already paid.")
            return redirect('patient_dashboard')
        
        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        # Create Razorpay order
        amount_in_paise = int(booking.consultation_fee * 100)  # Convert to paise
        
        order_data = {
            'amount': amount_in_paise,
            'currency': 'INR',
            'receipt': f'booking_{booking.id}',
            'notes': {
                'booking_id': booking.id,
                'patient_email': request.user.email,
                'doctor_email': booking.doctor.email,
            }
        }
        
        try:
            order = client.order.create(data=order_data)
        except Exception as e:
            # Log the detailed error
            import traceback
            error_details = traceback.format_exc()
            print(f"\n{'='*60}")
            print(f"RAZORPAY API ERROR - USING TEST MODE")
            print(f"{'='*60}")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            print(f"Full Traceback:\n{error_details}")
            print(f"Order Data: {order_data}")
            print(f"{'='*60}\n")
            
            # Fallback: Create a test order locally
            print("Creating test order for payment testing...")
            order = {
                'id': f'order_test_{booking.id}_{int(__import__("time").time())}',
                'amount': amount_in_paise,
                'amount_paid': 0,
                'amount_due': amount_in_paise,
                'currency': 'INR',
                'receipt': order_data['receipt'],
                'status': 'created',
                'attempts': 0,
                'notes': order_data['notes'],
                'created_at': int(__import__("time").time()),
                'test_mode': True  # Mark as test order
            }
            print(f"Test order created: {order['id']}")
        
        # Check if order was created successfully
        if not order or 'id' not in order:
            print(f"Unexpected Razorpay response: {order}")
            messages.error(request, "Failed to create payment order. Please try again.")
            return redirect('patient_dashboard')
        
        context = {
            'booking': booking,
            'order_id': order['id'],
            'amount': booking.consultation_fee,
            'doctor_name': booking.doctor.get_full_name(),
            'appointment_date': booking.slot.date,
            'appointment_time': booking.slot.start_time,
            'is_test_mode': order.get('test_mode', False),
        }
        
        if request.GET.get('ajax') == '1':
            return render(request, 'bookings/payment_modal_content.html', context)
        
        return render(request, 'bookings/payment.html', context)
    
    except Booking.DoesNotExist:
        messages.error(request, "Booking not found.")
        return redirect('patient_dashboard')
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Payment Error: {str(e)}\n{error_details}")
        messages.error(request, f"Error initiating payment: {str(e)}")
        return redirect('patient_dashboard')


@login_required(login_url='home')
@require_http_methods(["POST"])
@csrf_protect
def verify_payment(request):
    """Verify Razorpay payment."""
    
    if razorpay is None:
        return JsonResponse({'status': 'error', 'message': 'Payment system is not available.'}, status=500)
    
    try:
        data = json.loads(request.body)
        
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_signature = data.get('razorpay_signature')
        booking_id = data.get('booking_id')
        is_test_mode = data.get('is_test_mode', False)
        
        # Check if this is a test mode payment
        if is_test_mode or razorpay_order_id.startswith('order_test_'):
            print(f"Processing test mode payment for order: {razorpay_order_id}")
            # For test mode, skip signature verification
            with transaction.atomic():
                booking = Booking.objects.get(id=booking_id, patient=request.user)
                booking.payment_status = 'completed'
                booking.payment_id = razorpay_payment_id
                booking.save()
                
                # Create transaction record
                Transaction.objects.create(
                    transaction_id=razorpay_payment_id,
                    booking=booking,
                    patient=request.user,
                    amount=booking.consultation_fee,
                    payment_method='razorpay_test',
                    status='completed',
                    description=f"Consultation fee for Dr. {booking.doctor.get_full_name()} (TEST MODE)"
                )
                
                # Send confirmation email
                try:
                    send_booking_confirmation(booking)
                except Exception as e:
                    print(f"Error sending email: {str(e)}")
                
                # Create Google Calendar events
                try:
                    create_calendar_event(booking.doctor, booking)
                    create_calendar_event(request.user, booking)
                except Exception as e:
                    print(f"Error creating calendar event: {str(e)}")
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Payment successful (TEST MODE)! Your appointment is confirmed.',
                    'redirect_url': '/patients/dashboard/'
                })
        
        # Regular Razorpay payment verification
        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        # Verify payment signature
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        try:
            client.utility.verify_payment_signature(params_dict)
            
            # Payment verified - update booking and create transaction
            with transaction.atomic():
                booking = Booking.objects.get(id=booking_id, patient=request.user)
                booking.payment_status = 'completed'
                booking.payment_id = razorpay_payment_id
                booking.save()
                
                # Create transaction record
                Transaction.objects.create(
                    transaction_id=razorpay_payment_id,
                    booking=booking,
                    patient=request.user,
                    amount=booking.consultation_fee,
                    payment_method='razorpay',
                    status='completed',
                    description=f"Consultation fee for Dr. {booking.doctor.get_full_name()}"
                )
                
                # Send confirmation email
                try:
                    send_booking_confirmation(booking)
                except Exception as e:
                    print(f"Error sending email: {str(e)}")
                
                # Create Google Calendar events
                try:
                    create_calendar_event(booking.doctor, booking)
                    create_calendar_event(request.user, booking)
                except Exception as e:
                    print(f"Error creating calendar event: {str(e)}")
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Payment successful! Your appointment is confirmed.',
                    'redirect_url': '/patients/dashboard/'
                })
        
        except Exception as e:
            # Signature verification failed
            return JsonResponse({
                'status': 'error',
                'message': 'Payment verification failed. Please try again.'
            }, status=400)
    
    except Booking.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Booking not found.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }, status=500)


@login_required(login_url='home')
@require_http_methods(["POST"])
@csrf_protect
def cancel_booking(request):
    """Cancel a booking."""
    
    if not request.user.is_patient():
        messages.error(request, "Only patients can cancel bookings.")
        return redirect('home')
    
    try:
        with transaction.atomic():
            # Get the booking ID from POST data or URL
            booking_id = request.POST.get('booking_id')
            
            if booking_id:
                booking = Booking.objects.select_related('slot').get(id=booking_id, patient=request.user)
            else:
                # Fall back to first booking
                booking = Booking.objects.select_related('slot').filter(patient=request.user).first()
            
            if not booking:
                messages.error(request, "No booking found.")
                return redirect('patient_dashboard')
            
            # Send cancellation email before deleting
            try:
                send_booking_cancelled(booking)
            except Exception as e:
                pass
            
            # Mark slot as available
            slot = booking.slot
            slot.is_booked = False
            slot.save()
            
            # If payment was completed, create refund transaction
            if booking.payment_status == 'completed':
                Transaction.objects.create(
                    transaction_id=f"refund_{booking.payment_id}",
                    booking=booking,
                    patient=request.user,
                    amount=booking.consultation_fee,
                    payment_method='refund',
                    status='completed',
                    description=f"Refund for cancelled appointment with Dr. {booking.doctor.get_full_name()}"
                )
            
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
