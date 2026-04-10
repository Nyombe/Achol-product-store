import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

client = Client()

urls_to_test = [
    '/',
    '/products/',
    '/auth/login/',
    '/auth/register/',
    '/cart/',
    '/about/',
    '/contact/',
    '/admin/',
]

print("Testing Main URLs...")
has_error = False
for url in urls_to_test:
    try:
        response = client.get(url)
        print(f"URL: {url} -> Status: {response.status_code}")
        if response.status_code >= 400:
            print("ERROR response start:")
            print(response.content.decode('utf-8')[:800])
            has_error = True
    except Exception as e:
        print(f"URL: {url} -> CRASH: {str(e)}")
        has_error = True

# Also test a product page if one exists
from products.models import Product
p = Product.objects.first()
if p:
    print(f"\nTesting Product URL: {p.get_absolute_url()}")
    try:
        response = client.get(p.get_absolute_url())
        print(f"Status: {response.status_code}")
        if response.status_code >= 400:
            print("ERROR response start:")
            print(response.content.decode('utf-8')[:800])
            has_error = True
    except Exception as e:
        print(f"CRASH: {str(e)}")
        has_error = True
