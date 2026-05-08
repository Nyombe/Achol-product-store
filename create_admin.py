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
    admin_password = 'AcholAdmin2024!'
    admin_email = 'admin@achol.com'

    # Handle User
    user = CustomUser.objects.filter(username=admin_username).first()
    if user:
        print(f"Updating existing admin: {admin_username}")
        user.set_password(admin_password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
    else:
        print(f"Creating new admin: {admin_username}")
        CustomUser.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password
        )

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
