"""Management command to seed departments and specializations."""
from django.core.management.base import BaseCommand
from admin_management.models import Department, Specialization


class Command(BaseCommand):
    """Seed departments and specializations command."""
    
    help = 'Seed database with departments and medical specializations'
    
    def handle(self, *args, **options):
        """Handle command execution."""
        
        # Define departments
        departments_data = [
            {
                'name': 'Cardiology',
                'code': 'CARD',
                'description': 'Heart and cardiovascular system treatments',
            },
            {
                'name': 'Neurology',
                'code': 'NEUR',
                'description': 'Brain, spine, and nervous system treatments',
            },
            {
                'name': 'Orthopedics',
                'code': 'ORTH',
                'description': 'Bones, joints, and musculoskeletal treatments',
            },
            {
                'name': 'Pediatrics',
                'code': 'PEDI',
                'description': 'Child health and development care',
            },
            {
                'name': 'General Medicine',
                'code': 'GENM',
                'description': 'General health and internal medicine',
            },
            {
                'name': 'Surgery',
                'code': 'SURG',
                'description': 'Surgical procedures and treatments',
            },
            {
                'name': 'Dermatology',
                'code': 'DERM',
                'description': 'Skin and dermatological treatments',
            },
            {
                'name': 'Psychiatry',
                'code': 'PSYC',
                'description': 'Mental health and psychiatric care',
            },
            {
                'name': 'Ophthalmology',
                'code': 'OPHT',
                'description': 'Eye and vision care',
            },
            {
                'name': 'ENT (Otolaryngology)',
                'code': 'ENT',
                'description': 'Ear, nose, and throat treatments',
            },
        ]
        
        # Define specializations
        specializations_data = [
            # Cardiology
            {'name': 'General Cardiology', 'dept': 'Cardiology', 'base_fee': 500, 'consultation_fee': 300},
            {'name': 'Interventional Cardiology', 'dept': 'Cardiology', 'base_fee': 800, 'consultation_fee': 500},
            {'name': 'Cardiac Surgery', 'dept': 'Cardiology', 'base_fee': 1000, 'consultation_fee': 600},
            
            # Neurology
            {'name': 'General Neurology', 'dept': 'Neurology', 'base_fee': 500, 'consultation_fee': 300},
            {'name': 'Neurological Surgery', 'dept': 'Neurology', 'base_fee': 900, 'consultation_fee': 600},
            {'name': 'Pediatric Neurology', 'dept': 'Neurology', 'base_fee': 400, 'consultation_fee': 250},
            
            # Orthopedics
            {'name': 'General Orthopedics', 'dept': 'Orthopedics', 'base_fee': 400, 'consultation_fee': 250},
            {'name': 'Orthopedic Surgery', 'dept': 'Orthopedics', 'base_fee': 700, 'consultation_fee': 450},
            {'name': 'Sports Medicine', 'dept': 'Orthopedics', 'base_fee': 500, 'consultation_fee': 300},
            
            # Pediatrics
            {'name': 'General Pediatrics', 'dept': 'Pediatrics', 'base_fee': 300, 'consultation_fee': 200},
            {'name': 'Pediatric Cardiology', 'dept': 'Pediatrics', 'base_fee': 600, 'consultation_fee': 400},
            {'name': 'Neonatology', 'dept': 'Pediatrics', 'base_fee': 400, 'consultation_fee': 300},
            
            # General Medicine
            {'name': 'General Physician', 'dept': 'General Medicine', 'base_fee': 250, 'consultation_fee': 150},
            {'name': 'Gastroenterology', 'dept': 'General Medicine', 'base_fee': 500, 'consultation_fee': 300},
            {'name': 'Pulmonology', 'dept': 'General Medicine', 'base_fee': 450, 'consultation_fee': 280},
            {'name': 'Nephrology', 'dept': 'General Medicine', 'base_fee': 500, 'consultation_fee': 300},
            
            # Surgery
            {'name': 'General Surgery', 'dept': 'Surgery', 'base_fee': 600, 'consultation_fee': 400},
            {'name': 'Vascular Surgery', 'dept': 'Surgery', 'base_fee': 800, 'consultation_fee': 500},
            {'name': 'Laparoscopic Surgery', 'dept': 'Surgery', 'base_fee': 700, 'consultation_fee': 450},
            
            # Dermatology
            {'name': 'General Dermatology', 'dept': 'Dermatology', 'base_fee': 350, 'consultation_fee': 200},
            {'name': 'Cosmetic Dermatology', 'dept': 'Dermatology', 'base_fee': 500, 'consultation_fee': 300},
            {'name': 'Dermatological Surgery', 'dept': 'Dermatology', 'base_fee': 600, 'consultation_fee': 400},
            
            # Psychiatry
            {'name': 'General Psychiatry', 'dept': 'Psychiatry', 'base_fee': 400, 'consultation_fee': 250},
            {'name': 'Child Psychiatry', 'dept': 'Psychiatry', 'base_fee': 350, 'consultation_fee': 200},
            {'name': 'Clinical Psychology', 'dept': 'Psychiatry', 'base_fee': 300, 'consultation_fee': 180},
            
            # Ophthalmology
            {'name': 'General Ophthalmology', 'dept': 'Ophthalmology', 'base_fee': 300, 'consultation_fee': 150},
            {'name': 'Cornea and Refractive Surgery', 'dept': 'Ophthalmology', 'base_fee': 700, 'consultation_fee': 450},
            {'name': 'Retinal Surgery', 'dept': 'Ophthalmology', 'base_fee': 800, 'consultation_fee': 500},
            
            # ENT
            {'name': 'General ENT', 'dept': 'ENT (Otolaryngology)', 'base_fee': 300, 'consultation_fee': 150},
            {'name': 'ENT Surgery', 'dept': 'ENT (Otolaryngology)', 'base_fee': 600, 'consultation_fee': 400},
            {'name': 'Otology', 'dept': 'ENT (Otolaryngology)', 'base_fee': 500, 'consultation_fee': 300},
        ]
        
        # Create departments
        departments_dict = {}
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults={
                    'name': dept_data['name'],
                    'description': dept_data['description'],
                    'status': 'active',
                    'is_active': True,
                }
            )
            departments_dict[dept_data['name']] = dept
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Department created: {dept.name} ({dept.code})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'~ Department already exists: {dept.name}')
                )
        
        # Create specializations
        for spec_data in specializations_data:
            department = departments_dict.get(spec_data['dept'])
            
            spec, created = Specialization.objects.get_or_create(
                name=spec_data['name'],
                defaults={
                    'department': department,
                    'base_fee': spec_data['base_fee'],
                    'consultation_fee': spec_data['consultation_fee'],
                    'description': f"{spec_data['name']} specialization",
                    'status': 'active',
                    'is_active': True,
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ Specialization created: {spec.name} '
                        f'(₹{spec.consultation_fee} consultation fee)'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  ~ Specialization already exists: {spec.name}')
                )
        
        # Summary
        total_departments = Department.objects.count()
        total_specializations = Specialization.objects.count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Seeding complete!\n'
                f'  Departments: {total_departments}\n'
                f'  Specializations: {total_specializations}'
            )
        )
