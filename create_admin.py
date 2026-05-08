#!/usr/bin/env python
import os
import django
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Use environment variable or default to base
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.development')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
django.setup()

from users.models import CustomUser
from django_otp.plugins.otp_totp.models import TOTPDevice

print(f"Running admin reset with {settings_module}...")

# 1. Clean up existing admin if it exists
admin_username = 'admin'
admin_password = 'AcholAdmin2024!'

print(f"Updating account for: {admin_username}")
user = CustomUser.objects.filter(username=admin_username).first()

if user:
    user.set_password(admin_password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print("✓ Existing admin password updated.")
else:
    admin = CustomUser.objects.create_superuser(
        username=admin_username,
        email='admin@achol.com',
        password=admin_password
    )
    print("✓ New superuser created successfully!")

# 2. Ensure MFA/OTP is cleared for a fresh start
TOTPDevice.objects.filter(user__username=admin_username).delete()
print("✓ MFA/OTP devices cleared. You can now login with just password.")
