"""Debug script to check user credentials."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import CustomUser

email = 'ankita.pawarr19@gmail.com'
password = 'Admin@1904'

print("\n" + "="*50)
print("USER CREDENTIAL DEBUG")
print("="*50)

# Check if user exists
try:
    user = CustomUser.objects.get(email__iexact=email)
    print(f"\n✓ User found: {user.email}")
    print(f"  Username: {user.username}")
    print(f"  Full Name: {user.get_full_name()}")
    print(f"  Role: {user.role}")
    print(f"  Is Staff: {user.is_staff}")
    print(f"  Is Superuser: {user.is_superuser}")
    
    # Check if password is correct
    if user.check_password(password):
        print(f"\n✓ Password is CORRECT")
    else:
        print(f"\n✗ Password is INCORRECT")
        print(f"  Stored hash: {user.password[:50]}...")
        print(f"\n  To fix: Run this command:")
        print(f"  python manage.py create_demo_users")
    
except CustomUser.DoesNotExist:
    print(f"\n✗ User NOT found with email: {email}")
    print(f"\n  To create user, run:")
    print(f"  python manage.py create_demo_users")

print("\n" + "="*50 + "\n")
