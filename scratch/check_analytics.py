import os
import django
from django.conf import settings
from django.template.loader import get_template
from django.urls import reverse, resolve

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

print("--- Settings Check ---")
print(f"DEBUG: {settings.DEBUG}")
print(f"INSTALLED_APPS: {settings.INSTALLED_APPS}")
print(f"JAZZMIN_SETTINGS (dashboard_view): {settings.JAZZMIN_SETTINGS.get('dashboard_view')}")

print("\n--- URL Resolution ---")
try:
    url = reverse('admin:index')
    print(f"admin:index -> {url}")
    resolved = resolve(url)
    print(f"Resolved function: {resolved.func}")
except Exception as e:
    print(f"URL Error: {e}")

print("\n--- Template Check ---")
try:
    template = get_template("admin/index.html")
    print(f"admin/index.html origin: {template.origin.name}")
except Exception as e:
    print(f"Template Error: {e}")
