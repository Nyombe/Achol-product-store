from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Category, Product, ProductImage
from decimal import Decimal
import os

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for development and testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))

        # Create superuser
        if not User.objects.filter(email='admin@ecommerce.com').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@ecommerce.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS('✓ Superuser created'))

        # Create categories
        categories = [
            {'name': 'Electronics', 'description': 'Electronic devices and gadgets'},
            {'name': 'Clothing', 'description': 'Apparel and fashion items'},
            {'name': 'Home & Garden', 'description': 'Home and garden products'},
            {'name': 'Sports', 'description': 'Sports and outdoor equipment'},
            {'name': 'Books', 'description': 'Books and e-books'},
        ]

        created_categories = {}
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            created_categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'✓ Created category: {category.name}')

        # Create sample products
        products_data = [
            {
                'name': 'Wireless Headphones',
                'category': 'Electronics',
                'price': Decimal('79.99'),
                'discount_price': Decimal('59.99'),
                'stock': 50,
                'sku': 'WH-001',
                'brand': 'AudioTech',
                'description': 'High-quality wireless headphones with noise cancellation'
            },
            {
                'name': 'Smart Watch',
                'category': 'Electronics',
                'price': Decimal('199.99'),
                'discount_price': Decimal('149.99'),
                'stock': 30,
                'sku': 'SW-001',
                'brand': 'TechBrand',
                'description': 'Advanced smartwatch with health tracking features'
            },
            {
                'name': 'Running Shoes',
                'category': 'Sports',
                'price': Decimal('89.99'),
                'discount_price': None,
                'stock': 100,
                'sku': 'RS-001',
                'brand': 'AthleticWear',
                'description': 'Professional running shoes for all terrains'
            },
            {
                'name': 'Cotton T-Shirt',
                'category': 'Clothing',
                'price': Decimal('19.99'),
                'discount_price': Decimal('14.99'),
                'stock': 200,
                'sku': 'CT-001',
                'brand': 'FashionBrand',
                'description': 'Comfortable 100% cotton t-shirt'
            },
            {
                'name': 'Python Programming Book',
                'category': 'Books',
                'price': Decimal('49.99'),
                'discount_price': Decimal('39.99'),
                'stock': 75,
                'sku': 'PB-001',
                'brand': 'TechPress',
                'description': 'Comprehensive guide to Python programming'
            },
        ]

        for prod_data in products_data:
            category = created_categories[prod_data['category']]
            product, created = Product.objects.get_or_create(
                sku=prod_data['sku'],
                defaults={
                    'name': prod_data['name'],
                    'category': category,
                    'price': prod_data['price'],
                    'discount_price': prod_data['discount_price'],
                    'stock': prod_data['stock'],
                    'brand': prod_data['brand'],
                    'description': prod_data['description'],
                }
            )
            if created:
                self.stdout.write(f'✓ Created product: {product.name}')

        self.stdout.write(self.style.SUCCESS('\n✓ Sample data creation completed!'))
        self.stdout.write(self.style.WARNING('\nDevelopment User:'))
        self.stdout.write(f'Email: admin@ecommerce.com')
        self.stdout.write(f'Password: admin123')
