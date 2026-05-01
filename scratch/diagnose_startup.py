import os
import django
import sys
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
os.environ.setdefault('SECRET_KEY', 'fake-key-for-debug')
os.environ.setdefault('DATABASE_URL', 'sqlite:///db.sqlite3') # Use sqlite for local test

try:
    print("Starting Django setup...")
    django.setup()
    print("Django setup successful!")
    
    print("Loading URLs...")
    from django.urls import get_resolver
    patterns = get_resolver().url_patterns
    print(f"URLs loaded successful! Found {len(patterns)} patterns.")
    
    print("Checking system...")
    from django.core.management import call_command
    call_command('check')
    print("System check successful!")

except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
