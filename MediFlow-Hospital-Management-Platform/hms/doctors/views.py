"""Views for doctors app."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta, datetime
from .models import (
    AvailabilitySlot, ConsultationNote, Prescription, Earning, 
    DoctorRating, TelemedicineSession, MedicalHistory
)
from .forms import AvailabilitySlotForm
from bookings.models import Booking


def doctor_only(view_func):
    """Decorator to check if user is a doctor."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_doctor():
            messages.error(request, "You don't have permission to access this page.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required(login_url='home')
@doctor_only
def doctor_dashboard(request):
    """Enhanced doctor dashboard view with all statistics."""
    doctor = request.user
    today = timezone.now().date()
    
    # Bookings statistics
    all_bookings = Booking.objects.filter(doctor=doctor).select_related('patient', 'slot')
    total_bookings = all_bookings.count()
    
    # Today's appointments
    today_bookings = all_bookings.filter(slot__date=today)
    today_count = today_bookings.count()
    
    # Weekly appointments
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    weekly_bookings = all_bookings.filter(slot__date__range=[week_start, week_end])
    weekly_count = weekly_bookings.count()
    
    # Monthly appointments  
    month_start = today.replace(day=1)
    if today.month == 12:
        month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    monthly_bookings = all_bookings.filter(slot__date__range=[month_start, month_end])
    monthly_count = monthly_bookings.count()
    
    # Earnings
    total_earnings = Earning.objects.filter(doctor=doctor, payment_status='COMPLETED').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Consultation statistics
    completed_consultations = ConsultationNote.objects.filter(doctor=doctor).count()
    pending_followups = ConsultationNote.objects.filter(doctor=doctor, followup_required=True).count()
    
    # Patient count
    unique_patients = all_bookings.values('patient').distinct().count()
    
    # Ratings
    avg_rating = DoctorRating.objects.filter(doctor=doctor).aggregate(avg=Avg('rating'))['avg'] or 0
    total_ratings = DoctorRating.objects.filter(doctor=doctor).count()
    
    # Slots information
    available_slots = AvailabilitySlot.objects.filter(doctor=doctor, is_booked=False).count()
    booked_slots = AvailabilitySlot.objects.filter(doctor=doctor, is_booked=True).count()
    
    # Recent activity
    recent_bookings = all_bookings.order_by('-created_at')[:5]
    recent_consultations = ConsultationNote.objects.filter(doctor=doctor).order_by('-created_at')[:3]
    recent_prescriptions = Prescription.objects.filter(doctor=doctor).order_by('-created_at')[:3]
    upcoming_appointments = all_bookings.filter(slot__date__gte=today).order_by('slot__date', 'slot__start_time')[:5]
    
    context = {
        # Statistics
        'today_count': today_count,
        'weekly_count': weekly_count,
        'monthly_count': monthly_count,
        'total_bookings': total_bookings,
        'unique_patients': unique_patients,
        'total_earnings': total_earnings,
        'completed_consultations': completed_consultations,
        'pending_followups': pending_followups,
        'available_slots': available_slots,
        'booked_slots': booked_slots,
        'avg_rating': f"{avg_rating:.1f}",
        'total_ratings': total_ratings,
        
        # Recent data
        'recent_bookings': recent_bookings,
        'recent_consultations': recent_consultations,
        'recent_prescriptions': recent_prescriptions,
        'upcoming_appointments': upcoming_appointments,
    }
    
    # Handle AJAX requests
    if request.GET.get('ajax') == '1':
        return render(request, 'doctors/dashboard_content.html', context)
    
    return render(request, 'doctors/dashboard.html', context)


@login_required(login_url='home')
@doctor_only
def appointments_management(request):
    """View and manage all appointments."""
    doctor = request.user
    appointments = Booking.objects.filter(doctor=doctor).select_related('patient', 'slot').order_by('-created_at')
    
    # Filtering
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    search = request.GET.get('search', '')
    
    if status_filter:
        # Filter by status - would need additional status field in Booking model
        pass
    if date_filter:
        appointments = appointments.filter(slot__date=date_filter)
    if search:
        appointments = appointments.filter(
            Q(patient__first_name__icontains=search) |
            Q(patient__last_name__icontains=search) |
            Q(patient__email__icontains=search)
        )
    
    context = {
        'appointments': appointments,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'search': search,
    }
    
    return render(request, 'doctors/appointments.html', context)


@login_required(login_url='home')
@doctor_only
def add_consultation_note(request, booking_id):
    """Add or edit consultation notes after appointment."""
    booking = get_object_or_404(Booking, id=booking_id, doctor=request.user)
    
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        followup_required = request.POST.get('followup_required') == 'on'
        followup_date = request.POST.get('followup_date', None)
        
        ConsultationNote.objects.update_or_create(
            doctor=request.user,
            patient=booking.patient,
            appointment_date=timezone.now(),
            defaults={
                'notes': notes,
                'followup_required': followup_required,
                'followup_date': followup_date,
            }
        )
        messages.success(request, "Consultation notes saved successfully.")
        return redirect('doctor_dashboard')
    
    consultation = ConsultationNote.objects.filter(
        doctor=request.user,
        patient=booking.patient
    ).first()
    
    context = {
        'booking': booking,
        'consultation': consultation,
    }
    
    return render(request, 'doctors/add_note.html', context)


@login_required(login_url='home')
@doctor_only
def prescription_management(request):
    """View and create prescriptions."""
    prescriptions = Prescription.objects.filter(doctor=request.user).order_by('-created_at')
    
    context = {
        'prescriptions': prescriptions,
    }
    
    return render(request, 'doctors/prescriptions.html', context)


@login_required(login_url='home')
@doctor_only
def create_prescription(request):
    """Create a new prescription."""
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        diagnosis = request.POST.get('diagnosis')
        medicines_data = request.POST.get('medicines_json')  # JSON array
        instructions = request.POST.get('instructions')
        valid_until = request.POST.get('valid_until')
        
        import json
        medicines = json.loads(medicines_data) if medicines_data else []
        
        prescription = Prescription.objects.create(
            doctor=request.user,
            patient_id=patient_id,
            diagnosis=diagnosis,
            medicines=medicines,
            instructions=instructions,
            valid_until=valid_until,
            digital_signature=f"DR-{request.user.id}-{timezone.now().timestamp()}"
        )
        
        messages.success(request, "Prescription created successfully.")
        return redirect('prescription_management')
    
    # Get list of patients this doctor has consulted
    patients = Booking.objects.filter(doctor=request.user).values_list(
        'patient', flat=True
    ).distinct()
    from accounts.models import CustomUser
    patient_list = CustomUser.objects.filter(id__in=patients, role='PATIENT')
    
    context = {
        'patients': patient_list,
    }
    
    return render(request, 'doctors/create_prescription.html', context)


@login_required(login_url='home')
@doctor_only
def earnings_dashboard(request):
    """View earnings and payment information."""
    earnings = Earning.objects.filter(doctor=request.user).order_by('-created_at')
    
    # Analytics
    total_earnings = earnings.filter(payment_status='COMPLETED').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    pending_earnings = earnings.filter(payment_status='PENDING').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    completed_earnings = earnings.filter(payment_status='COMPLETED').count()
    pending_count = earnings.filter(payment_status='PENDING').count()
    
    # Monthly breakdown
    current_month = timezone.now().replace(day=1)
    monthly_earnings = earnings.filter(
        payment_status='COMPLETED',
        payment_date__gte=current_month
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'earnings': earnings[:50],
        'total_earnings': total_earnings,
        'pending_earnings': pending_earnings,
        'completed_count': completed_earnings,
        'pending_count': pending_count,
        'monthly_earnings': monthly_earnings,
    }
    
    return render(request, 'doctors/earnings.html', context)


@login_required(login_url='home')
@doctor_only
def patient_medical_history(request):
    """Access patient medical history and records."""
    doctor = request.user
    
    # Get all patients this doctor has consulted
    patients = Booking.objects.filter(doctor=doctor).values_list(
        'patient', flat=True
    ).distinct()
    
    histories = MedicalHistory.objects.filter(doctor=doctor).order_by('-diagnosis_date')
    
    context = {
        'histories': histories,
    }
    
    return render(request, 'doctors/medical_history.html', context)


@login_required(login_url='home')
@doctor_only
def add_medical_history(request, patient_id):
    """Add or update patient medical history."""
    from accounts.models import CustomUser
    patient = get_object_or_404(CustomUser, id=patient_id, role='PATIENT')
    
    if request.method == 'POST':
        condition = request.POST.get('condition')
        description = request.POST.get('description')
        diagnosis_date = request.POST.get('diagnosis_date')
        status = request.POST.get('status', 'active')
        
        MedicalHistory.objects.create(
            doctor=request.user,
            patient=patient,
            condition=condition,
            description=description,
            diagnosis_date=diagnosis_date,
            status=status,
        )
        
        messages.success(request, "Medical history added successfully.")
        return redirect('patient_medical_history')
    
    context = {
        'patient': patient,
    }
    
    return render(request, 'doctors/add_medical_history.html', context)


@login_required(login_url='home')
@doctor_only
def doctor_ratings(request):
    """View patient ratings and reviews."""
    ratings = DoctorRating.objects.filter(doctor=request.user).order_by('-created_at')
    
    avg_rating = ratings.aggregate(avg=Avg('rating'))['avg'] or 0
    rating_counts = {
        '5': ratings.filter(rating=5).count(),
        '4': ratings.filter(rating=4).count(),
        '3': ratings.filter(rating=3).count(),
        '2': ratings.filter(rating=2).count(),
        '1': ratings.filter(rating=1).count(),
    }
    
    context = {
        'ratings': ratings,
        'avg_rating': f"{avg_rating:.1f}",
        'total_ratings': ratings.count(),
        'rating_counts': rating_counts,
    }
    
    return render(request, 'doctors/ratings.html', context)


@login_required(login_url='home')
@doctor_only
def reply_to_review(request, rating_id):
    """Reply to a patient's review."""
    rating = get_object_or_404(DoctorRating, id=rating_id, doctor=request.user)
    
    if request.method == 'POST':
        response = request.POST.get('response')
        rating.response = response
        rating.save()
        messages.success(request, "Response posted successfully.")
        return redirect('doctor_ratings')
    
    context = {
        'rating': rating,
    }
    
    return render(request, 'doctors/reply_review.html', context)


@login_required(login_url='home')
@doctor_only
def create_availability(request):
    """Create availability slot."""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        form = AvailabilitySlotForm(request.POST, doctor=request.user)
        if form.is_valid():
            try:
                slot = form.save(commit=False)
                slot.doctor = request.user
                slot.save()
                messages.success(request, "Availability slot created successfully.")
                
                # For AJAX requests, return the empty form
                if is_ajax:
                    return render(request, 'doctors/create_availability_content.html', {'form': AvailabilitySlotForm(doctor=request.user)})
                # For regular requests, redirect to dashboard
                return redirect('doctor_dashboard')
            except Exception as e:
                # Fallback error handling for database integrity errors
                if 'UNIQUE constraint failed' in str(e):
                    messages.error(request, 
                        "You already have an availability slot with these exact date and times. "
                        "Please choose a different time or date.")
                else:
                    messages.error(request, "An error occurred while creating the slot. Please try again.")
    else:
        form = AvailabilitySlotForm(doctor=request.user)
    
    # Handle AJAX requests
    if is_ajax:
        return render(request, 'doctors/create_availability_content.html', {'form': form})
    
    return render(request, 'doctors/create_availability.html', {'form': form})


@login_required(login_url='home')
@doctor_only
def manage_availability(request):
    """Manage availability slots."""
    slots = AvailabilitySlot.objects.filter(doctor=request.user).order_by('-date', 'start_time')
    
    context = {
        'slots': slots,
    }
    
    # Handle AJAX requests
    if request.GET.get('ajax') == '1':
        return render(request, 'doctors/manage_availability_content.html', context)
    
    return render(request, 'doctors/manage_availability.html', context)


@login_required(login_url='home')
@doctor_only
@require_http_methods(["POST"])
def delete_availability(request, slot_id):
    """Delete availability slot."""
    slot = get_object_or_404(AvailabilitySlot, id=slot_id, doctor=request.user)
    
    if slot.is_booked:
        messages.error(request, "Cannot delete a booked slot.")
        if request.GET.get('ajax') == '1':
            slots = AvailabilitySlot.objects.filter(doctor=request.user).order_by('-date', 'start_time')
            return render(request, 'doctors/manage_availability_content.html', {'slots': slots})
        return redirect('manage_availability')
    
    slot.delete()
    messages.success(request, "Availability slot deleted successfully.")
    
    # Handle AJAX requests
    if request.GET.get('ajax') == '1':
        slots = AvailabilitySlot.objects.filter(doctor=request.user).order_by('-date', 'start_time')
        return render(request, 'doctors/manage_availability_content.html', {'slots': slots})
    
    return redirect('manage_availability')


@login_required(login_url='home')
@login_required(login_url='home')
@doctor_only
def view_bookings(request):
    """View doctor's bookings."""
    bookings = Booking.objects.filter(doctor=request.user).select_related(
        'patient', 'slot'
    ).order_by('-created_at')
    
    context = {
        'bookings': bookings,
    }
    
    # Handle AJAX requests
    if request.GET.get('ajax') == '1':
        return render(request, 'doctors/view_bookings_content.html', context)
    
    return render(request, 'doctors/view_bookings.html', context)


@login_required(login_url='home')
@doctor_only
def edit_doctor_profile(request):
    """Edit doctor profile."""
    from .forms import EditDoctorProfileForm
    
    if request.method == 'POST':
        form = EditDoctorProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            if request.GET.get('ajax') == '1':
                return render(request, 'doctors/edit_profile_content.html', {
                    'form': EditDoctorProfileForm(instance=request.user),
                    'doctor': request.user
                })
            return redirect('doctor_dashboard')
    else:
        form = EditDoctorProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'doctor': request.user,
    }
    
    # Handle AJAX requests
    if request.GET.get('ajax') == '1':
        return render(request, 'doctors/edit_profile_content.html', context)
    
    return render(request, 'doctors/edit_profile.html', context)


@login_required(login_url='home')
@doctor_only
def upload_patient_report(request):
    """Upload patient medical report."""
    from .forms import UploadPatientReportForm
    
    if request.method == 'POST':
        form = UploadPatientReportForm(doctor=request.user, data=request.POST, files=request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.doctor = request.user
            report.save()
            messages.success(request, "Patient report uploaded successfully!")
            if request.GET.get('ajax') == '1':
                return render(request, 'doctors/upload_report_content.html', {
                    'form': UploadPatientReportForm(doctor=request.user),
                    'reports': MedicalHistory.objects.filter(doctor=request.user).order_by('-created_at')[:10]
                })
            return redirect('doctor_dashboard')
    else:
        form = UploadPatientReportForm(doctor=request.user)
    
    # Get recent reports
    recent_reports = MedicalHistory.objects.filter(doctor=request.user).select_related('patient').order_by('-created_at')[:10]
    
    context = {
        'form': form,
        'recent_reports': recent_reports,
    }
    
    # Handle AJAX requests
    if request.GET.get('ajax') == '1':
        return render(request, 'doctors/upload_report_content.html', context)
    
    return render(request, 'doctors/upload_report.html', context)
