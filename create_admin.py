#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from users.models import CustomUser

# Delete existing admin
CustomUser.objects.filter(username='admin').delete()

# Create fresh superuser
admin = CustomUser.objects.create_superuser(
    username='admin',
    email='admin@ecommerce.com',
    password='admin123'
)

print("✓ Superuser created successfully!")
print(f"  Username: {admin.username}")
print(f"  Email: {admin.email}")
print(f"  is_staff: {admin.is_staff}")
print(f"  is_superuser: {admin.is_superuser}")
print(f"  is_active: {admin.is_active}")
