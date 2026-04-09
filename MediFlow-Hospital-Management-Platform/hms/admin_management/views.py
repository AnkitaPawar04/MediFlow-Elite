from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.http import JsonResponse
from accounts.models import CustomUser
from bookings.models import Booking
from .models import DoctorApproval, SystemAuditLog, Department, Specialization, Transaction


def is_admin(user):
    """Check if user is admin"""
    return user.is_staff or user.role == 'ADMIN'


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard with statistics"""
    context = {
        'total_users': CustomUser.objects.count(),
        'total_doctors': CustomUser.objects.filter(role='DOCTOR').count(),
        'total_patients': CustomUser.objects.filter(role='PATIENT').count(),
        'pending_approvals': DoctorApproval.objects.filter(status='pending').count(),
        'total_bookings': Booking.objects.count(),
        'pending_doctors': DoctorApproval.objects.filter(status='pending').select_related('doctor'),
        'recent_logs': SystemAuditLog.objects.all()[:10],
    }
    return render(request, 'admin_management/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def manage_users(request):
    """User management page with filtering and search"""
    users = CustomUser.objects.all()
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Filter by role
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(role=role_filter.upper())
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # Sorting
    sort_by = request.GET.get('sort', '-date_joined')
    users = users.order_by(sort_by)
    
    # Pagination would go here in production
    users = users[:100]  # Limit to 100 for demo
    
    context = {
        'users': users,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'total_count': CustomUser.objects.count(),
    }
    return render(request, 'admin_management/manage_users.html', context)


@login_required
@user_passes_test(is_admin)
def user_actions(request, user_id, action):
    """Handle user actions (activate, suspend, delete)"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    if action == 'suspend':
        user.is_active = False
        user.save()
        messages.success(request, f"{user.get_full_name()} has been suspended.")
        # Log action
        SystemAuditLog.objects.create(
            user=request.user,
            action='user_updated',
            description=f"Suspended user {user.email}"
        )
    elif action == 'activate':
        user.is_active = True
        user.save()
        messages.success(request, f"{user.get_full_name()} has been activated.")
        SystemAuditLog.objects.create(
            user=request.user,
            action='user_updated',
            description=f"Activated user {user.email}"
        )
    elif action == 'delete':
        name = user.get_full_name()
        email = user.email
        user.delete()
        messages.success(request, f"{name} has been deleted.")
        SystemAuditLog.objects.create(
            user=request.user,
            action='user_deleted',
            description=f"Deleted user {email}"
        )
        return redirect('admin_management:manage_users')
    
    return redirect('admin_management:manage_users')


@login_required
@user_passes_test(is_admin)
def manage_doctors(request):
    """Doctor management and approval page"""
    doctor_approvals = DoctorApproval.objects.select_related('doctor').filter(doctor__role='DOCTOR')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        doctor_approvals = doctor_approvals.filter(status=status_filter)
    
    # Statistics
    context = {
        'doctor_approvals': doctor_approvals,
        'pending_count': DoctorApproval.objects.filter(status='pending', doctor__role='DOCTOR').count(),
        'approved_count': DoctorApproval.objects.filter(status='approved', doctor__role='DOCTOR').count(),
        'suspended_count': DoctorApproval.objects.filter(status='suspended', doctor__role='DOCTOR').count(),
        'total_count': DoctorApproval.objects.filter(doctor__role='DOCTOR').count(),
        'status_filter': status_filter,
    }
    return render(request, 'admin_management/manage_doctors.html', context)


@login_required
@user_passes_test(is_admin)
def doctor_actions(request, approval_id, action):
    """Handle doctor approval actions"""
    approval = get_object_or_404(DoctorApproval, id=approval_id)
    doctor = approval.doctor
    
    # Log action
    log_actions = {
        'approve': 'doctor_approved',
        'suspend': 'doctor_suspended',
        'reject': 'doctor_updated',
    }
    
    if action == 'approve':
        approval.status = 'approved'
        approval.approved_at = timezone.now()
        approval.save()
        doctor.is_active = True
        doctor.save()
        messages.success(request, f"{doctor.get_full_name()} has been approved.")
        SystemAuditLog.objects.create(
            user=request.user,
            action='doctor_approved',
            description=f"Approved doctor {doctor.email}"
        )
    elif action == 'suspend':
        approval.status = 'suspended'
        approval.save()
        doctor.is_active = False
        doctor.save()
        messages.warning(request, f"{doctor.get_full_name()} has been suspended.")
        SystemAuditLog.objects.create(
            user=request.user,
            action='doctor_suspended',
            description=f"Suspended doctor {doctor.email}"
        )
    
    return redirect('admin_management:manage_doctors')


@login_required
@user_passes_test(is_admin)
def system_logs(request):
    """View system audit logs"""
    logs = SystemAuditLog.objects.all().order_by('-timestamp')
    
    # Filter by action
    action_filter = request.GET.get('action', '')
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    context = {
        'logs': logs[:500],  # Limit to 500 most recent
        'action_filter': action_filter,
    }
    return render(request, 'admin_management/system_logs.html', context)


@login_required
@user_passes_test(is_admin)
def departments(request):
    """Departments management with enhanced features"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()
        description = request.POST.get('description', '').strip()
        
        if name and code:
            department, created = Department.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'description': description,
                }
            )
            if created:
                messages.success(request, f"Department '{name}' created successfully.")
                SystemAuditLog.objects.create(
                    user=request.user,
                    action='user_updated',
                    description=f"Created department: {name} ({code})"
                )
            else:
                messages.warning(request, "Department code already exists.")
            return redirect('admin_management:departments')
    
    # Search and filter
    departments = Department.objects.all()
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    sort_by = request.GET.get('sort', 'name')
    
    if search_query:
        departments = departments.filter(
            Q(name__icontains=search_query) | 
            Q(code__icontains=search_query)
        )
    
    if status_filter:
        departments = departments.filter(status=status_filter)
    
    departments = departments.order_by(sort_by)
    
    # Statistics
    total_departments = Department.objects.count()
    active_departments = Department.objects.filter(status='active').count()
    
    context = {
        'departments': departments,
        'doctors': CustomUser.objects.filter(role='DOCTOR', is_active=True),
        'total_departments': total_departments,
        'active_departments': active_departments,
        'search_query': search_query,
        'status_filter': status_filter,
        'sort_by': sort_by,
    }
    return render(request, 'admin_management/departments.html', context)


@login_required
@user_passes_test(is_admin)
def department_detail(request, dept_id):
    """View department details with doctors and specializations"""
    from doctors.models import Doctor
    
    department = get_object_or_404(Department, id=dept_id)
    doctors = Doctor.objects.filter(department=department)
    department_specializations = Specialization.objects.filter(department=department)
    
    # Get appointment count
    from bookings.models import Booking
    appointment_count = Booking.objects.filter(doctor__in=doctors).count()
    
    context = {
        'department': department,
        'doctors': doctors,
        'department_specializations': department_specializations,
        'appointment_count': appointment_count,
    }
    return render(request, 'admin_management/department_detail.html', context)


@login_required
@user_passes_test(is_admin)
def department_actions(request, dept_id, action):
    """Handle department actions"""
    department = get_object_or_404(Department, id=dept_id)
    
    if action == 'edit':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()
        description = request.POST.get('description', '').strip()
        head_id = request.POST.get('head_of_department', '')
        
        if name and code:
            department.name = name
            department.code = code
            department.description = description
            if head_id:
                department.head_of_department_id = head_id
            department.save()
            messages.success(request, f"Department '{name}' updated successfully.")
            SystemAuditLog.objects.create(
                user=request.user,
                action='user_updated',
                description=f"Updated department: {name}"
            )
    
    elif action == 'toggle':
        new_status = 'inactive' if department.status == 'active' else 'active'
        department.status = new_status
        department.is_active = (new_status == 'active')
        department.save()
        messages.success(request, f"Department '{department.name}' is now {new_status}.")
        SystemAuditLog.objects.create(
            user=request.user,
            action='user_updated',
            description=f"Changed department status to {new_status}: {department.name}"
        )
    
    elif action == 'delete':
        name = department.name
        department.delete()
        messages.success(request, f"Department '{name}' deleted.")
        SystemAuditLog.objects.create(
            user=request.user,
            action='user_deleted',
            description=f"Deleted department: {name}"
        )
        return redirect('admin_management:departments')
    
    return redirect('admin_management:departments')


@login_required
@user_passes_test(is_admin)
def specializations(request):
    """Specializations management with enhanced features"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        base_fee = request.POST.get('base_fee', 0)
        consultation_fee = request.POST.get('consultation_fee', 0)
        dept_id = request.POST.get('department', '')
        
        if name:
            specialization, created = Specialization.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'base_fee': base_fee,
                    'consultation_fee': consultation_fee,
                    'department_id': dept_id if dept_id else None,
                }
            )
            if created:
                messages.success(request, f"Specialization '{name}' created successfully.")
                SystemAuditLog.objects.create(
                    user=request.user,
                    action='user_updated',
                    description=f"Created specialization: {name}"
                )
            else:
                messages.warning(request, "Specialization already exists.")
            return redirect('admin_management:specializations')
    
    # Search and filter
    specializations = Specialization.objects.all()
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    dept_filter = request.GET.get('department', '')
    sort_by = request.GET.get('sort', 'name')
    
    if search_query:
        specializations = specializations.filter(name__icontains=search_query)
    
    if status_filter:
        specializations = specializations.filter(status=status_filter)
    
    if dept_filter:
        specializations = specializations.filter(department_id=dept_filter)
    
    specializations = specializations.order_by(sort_by)
    
    # Statistics
    total_specializations = Specialization.objects.count()
    active_specializations = Specialization.objects.filter(status='active').count()
    
    context = {
        'specializations': specializations,
        'departments': Department.objects.all(),
        'total_specializations': total_specializations,
        'active_specializations': active_specializations,
        'search_query': search_query,
        'status_filter': status_filter,
        'dept_filter': dept_filter,
        'sort_by': sort_by,
    }
    return render(request, 'admin_management/specializations.html', context)


@login_required
@user_passes_test(is_admin)
def specialization_detail(request, spec_id):
    """View specialization details with doctors"""
    from doctors.models import Doctor
    
    specialization = get_object_or_404(Specialization, id=spec_id)
    doctors = Doctor.objects.filter(specialization=specialization)
    
    # Get related specializations (if department exists)
    related_specializations = []
    if specialization.department:
        related_specializations = Specialization.objects.filter(
            department=specialization.department
        ).exclude(id=specialization.id)
    
    # Count doctors
    doctors_count = doctors.count()
    
    # Count patient appointments
    from bookings.models import Booking
    patient_appointment_count = Booking.objects.filter(doctor__in=doctors).count()
    
    context = {
        'specialization': specialization,
        'doctors': doctors,
        'related_specializations': related_specializations,
        'doctors_count': doctors_count,
        'patient_appointment_count': patient_appointment_count,
        'departments': Department.objects.all(),  # For the edit modal
    }
    return render(request, 'admin_management/specialization_detail.html', context)


@login_required
@user_passes_test(is_admin)
def specialization_actions(request, spec_id, action):
    """Handle specialization actions"""
    specialization = get_object_or_404(Specialization, id=spec_id)
    
    if action == 'edit':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        base_fee = request.POST.get('base_fee', 0)
        consultation_fee = request.POST.get('consultation_fee', 0)
        dept_id = request.POST.get('department', '')
        
        if name:
            specialization.name = name
            specialization.description = description
            specialization.base_fee = base_fee
            specialization.consultation_fee = consultation_fee
            if dept_id:
                specialization.department_id = dept_id
            specialization.save()
            messages.success(request, f"Specialization '{name}' updated successfully.")
            SystemAuditLog.objects.create(
                user=request.user,
                action='user_updated',
                description=f"Updated specialization: {name}"
            )
    
    elif action == 'toggle':
        new_status = 'inactive' if specialization.status == 'active' else 'active'
        specialization.status = new_status
        specialization.is_active = (new_status == 'active')
        specialization.save()
        messages.success(request, f"Specialization '{specialization.name}' is now {new_status}.")
        SystemAuditLog.objects.create(
            user=request.user,
            action='user_updated',
            description=f"Changed specialization status to {new_status}: {specialization.name}"
        )
    
    elif action == 'delete':
        name = specialization.name
        specialization.delete()
        messages.success(request, f"Specialization '{name}' deleted.")
        SystemAuditLog.objects.create(
            user=request.user,
            action='user_deleted',
            description=f"Deleted specialization: {name}"
        )
        return redirect('admin_management:specializations')
    
    return redirect('admin_management:specializations')


@login_required
@user_passes_test(is_admin)
def transactions(request):
    """Transactions and payments"""
    transactions = Transaction.objects.all().order_by('-timestamp')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        transactions = transactions.filter(status=status_filter)
    
    # Filter by payment method
    method_filter = request.GET.get('method', '')
    if method_filter:
        transactions = transactions.filter(payment_method=method_filter)
    
    # Calculate statistics
    total_revenue = transactions.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    total_transactions = transactions.count()
    pending_amount = transactions.filter(status='pending').aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'transactions': transactions[:500],
        'status_filter': status_filter,
        'method_filter': method_filter,
        'total_revenue': total_revenue,
        'total_transactions': total_transactions,
        'pending_amount': pending_amount,
        'status_choices': Transaction._meta.get_field('status').choices,
        'method_choices': Transaction._meta.get_field('payment_method').choices,
    }
    return render(request, 'admin_management/transactions.html', context)


@login_required
@user_passes_test(is_admin)
def edit_profile(request):
    """Edit admin profile"""
    admin_user = request.user
    
    if request.method == 'POST':
        action = request.POST.get('action', 'update_profile')
        
        if action == 'update_profile':
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            
            admin_user.first_name = first_name
            admin_user.last_name = last_name
            admin_user.phone = phone
            # Only update email if it's different and not already taken
            if email != admin_user.email:
                if CustomUser.objects.filter(email=email).exists():
                    messages.error(request, "Email already in use.")
                    return redirect('admin_management:edit_profile')
                admin_user.email = email
            
            admin_user.save()
            messages.success(request, "Profile updated successfully.")
            SystemAuditLog.objects.create(
                user=request.user,
                action='user_updated',
                description="Admin updated their profile"
            )
        
        elif action == 'change_password':
            from django.contrib.auth.hashers import check_password, make_password
            old_password = request.POST.get('old_password', '')
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')
            
            if not check_password(old_password, admin_user.password):
                messages.error(request, "Old password is incorrect.")
            elif new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
            elif len(new_password) < 8:
                messages.error(request, "Password must be at least 8 characters.")
            else:
                admin_user.set_password(new_password)
                admin_user.save()
                messages.success(request, "Password changed successfully.")
                SystemAuditLog.objects.create(
                    user=request.user,
                    action='user_updated',
                    description="Admin changed their password"
                )
                return redirect('admin_management:edit_profile')
        
        return redirect('admin_management:edit_profile')
    
    context = {
        'admin_user': admin_user,
    }
    return render(request, 'admin_management/edit_profile.html', context)
