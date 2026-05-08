#!/usr/bin/env python
import os
import django
import sys
import traceback

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Use environment variable or default to base
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.production')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

try:
    django.setup()
    from users.models import CustomUser

    print(f"--- Admin Reset Started (Settings: {settings_module}) ---")

    admin_username = 'admin'
    admin_password = 'AcholLogin2024'
    admin_email = 'admin@achol.com'

    # Ensure we have a clean state for this specific admin
    print(f"Clearing existing admin state for {admin_username}...")
    CustomUser.objects.filter(username=admin_username).delete()
    CustomUser.objects.filter(email=admin_email).delete()

    print(f"Creating fresh admin: {admin_username} / {admin_email}")
    admin = CustomUser.objects.create_superuser(
        username=admin_username,
        email=admin_email,
        password=admin_password
    )
    admin.is_active = True
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()

    # Handle OTP Devices - Clear to allow password-only login
    try:
        from django_otp.plugins.otp_totp.models import TOTPDevice
        deleted_count, _ = TOTPDevice.objects.filter(user__username=admin_username).delete()
        print(f"✓ Cleared {deleted_count} OTP devices for admin.")
    except (ImportError, RuntimeError, Exception) as otp_err:
        print(f"--- Skipping OTP cleanup (App disabled or missing): {otp_err} ---")

    print("--- Admin Reset Completed Successfully ---")

except Exception as e:
    print("!!! ERROR DURING ADMIN RESET !!!")
    traceback.print_exc()
    # We exit with 0 so the build still completes even if this script fails
    # This prevents the whole site from going down due to a script error
    sys.exit(0)
