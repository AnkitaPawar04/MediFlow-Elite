"""Management command to create demo users for testing."""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import CustomUser

User = get_user_model()


class Command(BaseCommand):
    """Create demo users command."""
    
    help = 'Create demo admin, doctor, and patient users for testing'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--admin-email',
            type=str,
            default='ankita.pawarr19@gmail.com',
            help='Email for admin user (default: ankita.pawarr19@gmail.com)'
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            default='Admin@1904',
            help='Password for admin user (default: Admin@1904)'
        )
        parser.add_argument(
            '--doctor-email',
            type=str,
            default='doctor@mediflow.com',
            help='Email for demo doctor (default: doctor@mediflow.com)'
        )
        parser.add_argument(
            '--doctor-password',
            type=str,
            default='Doctor@12345',
            help='Password for demo doctor (default: Doctor@12345)'
        )
        parser.add_argument(
            '--patient-email',
            type=str,
            default='patient@mediflow.com',
            help='Email for demo patient (default: patient@mediflow.com)'
        )
        parser.add_argument(
            '--patient-password',
            type=str,
            default='Patient@12345',
            help='Password for demo patient (default: Patient@12345)'
        )
    
    def handle(self, *args, **options):
        """Handle command execution."""
        admin_email = options['admin_email'].lower()
        admin_password = options['admin_password']
        doctor_email = options['doctor_email'].lower()
        doctor_password = options['doctor_password']
        patient_email = options['patient_email'].lower()
        patient_password = options['patient_password']
        
        # Create or update admin user
        admin_user, admin_created = CustomUser.objects.get_or_create(
            email=admin_email,
            defaults={
                'username': admin_email,
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
                'role': 'ADMIN' if hasattr(CustomUser, 'ROLE_CHOICES') else 'DOCTOR',
            }
        )
        
        if not admin_created:
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.first_name = 'Admin'
            admin_user.last_name = 'User'
        
        admin_user.set_password(admin_password)
        admin_user.save()
        
        # Create or update demo doctor
        doctor_user, doctor_created = CustomUser.objects.get_or_create(
            email=doctor_email,
            defaults={
                'username': doctor_email,
                'first_name': 'Demo',
                'last_name': 'Doctor',
                'role': 'DOCTOR',
            }
        )
        
        if not doctor_created:
            doctor_user.first_name = 'Demo'
            doctor_user.last_name = 'Doctor'
            doctor_user.role = 'DOCTOR'
        
        doctor_user.set_password(doctor_password)
        doctor_user.save()
        
        # Create or update demo patient
        patient_user, patient_created = CustomUser.objects.get_or_create(
            email=patient_email,
            defaults={
                'username': patient_email,
                'first_name': 'Demo',
                'last_name': 'Patient',
                'role': 'PATIENT',
            }
        )
        
        if not patient_created:
            patient_user.first_name = 'Demo'
            patient_user.last_name = 'Patient'
            patient_user.role = 'PATIENT'
        
        patient_user.set_password(patient_password)
        patient_user.save()
        
        # Print credentials
        self.stdout.write(self.style.SUCCESS('\n✓ Demo users created/updated successfully!\n'))
        
        self.stdout.write(self.style.WARNING('Admin Credentials:'))
        self.stdout.write(f'  Email: {admin_email}')
        self.stdout.write(f'  Password: {admin_password}')
        self.stdout.write(f'  Access: http://127.0.0.1:8000/admin/\n')
        
        self.stdout.write(self.style.WARNING('Demo Doctor Credentials:'))
        self.stdout.write(f'  Email: {doctor_email}')
        self.stdout.write(f'  Password: {doctor_password}\n')
        
        self.stdout.write(self.style.WARNING('Demo Patient Credentials:'))
        self.stdout.write(f'  Email: {patient_email}')
        self.stdout.write(f'  Password: {patient_password}\n')
        
        self.stdout.write(self.style.SUCCESS('You can now login with these credentials!'))
