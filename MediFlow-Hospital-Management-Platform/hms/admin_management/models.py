from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import CustomUser

class Department(models.Model):
    """Hospital departments"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, db_index=True, default='DEPT')
    description = models.TextField(blank=True)
    head_of_department = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'DOCTOR'}, related_name='head_departments')
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Departments'
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def doctor_count(self):
        """Count doctors assigned to this department"""
        # TODO: Implement this when DoctorProfile model is added with department field
        return 0
    
    @property
    def patient_count(self):
        """Count patients who have appointments with doctors in this department"""
        # TODO: Implement this when DoctorProfile model is added with department field
        return 0


class Specialization(models.Model):
    """Medical specializations"""
    name = models.CharField(max_length=100, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='specializations')
    description = models.TextField(blank=True)
    base_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Specializations'
    
    def __str__(self):
        return self.name
    
    @property
    def doctor_count(self):
        """Count doctors with this specialization"""
        # TODO: Implement this when DoctorProfile model is added with specialization field
        return 0


class Transaction(models.Model):
    """Payment transactions"""
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('wallet', 'Wallet'),
        ('upi', 'UPI'),
        ('net_banking', 'Net Banking'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    transaction_id = models.CharField(max_length=100, unique=True)
    booking = models.ForeignKey('bookings.Booking', on_delete=models.SET_NULL, null=True, blank=True)
    patient = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'PATIENT'})
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Transactions'
    
    def __str__(self):
        return f"{self.transaction_id} - {self.amount}"


class DoctorApproval(models.Model):
    """Track doctor approval workflow"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('suspended', 'Suspended'),
    ]
    
    doctor = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor_approval', limit_choices_to={'role': 'DOCTOR'})
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    specialization = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Doctor Approval'
        verbose_name_plural = 'Doctor Approvals'
    
    def __str__(self):
        return f"{self.doctor.get_full_name()} - {self.status}"


class SystemAuditLog(models.Model):
    """Track system activities and changes"""
    ACTION_CHOICES = [
        ('user_created', 'User Created'),
        ('user_deleted', 'User Deleted'),
        ('user_updated', 'User Updated'),
        ('doctor_approved', 'Doctor Approved'),
        ('doctor_suspended', 'Doctor Suspended'),
        ('booking_created', 'Booking Created'),
        ('booking_cancelled', 'Booking Cancelled'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'System Audit Log'
        verbose_name_plural = 'System Audit Logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.timestamp}"
