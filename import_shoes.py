import os
import django
import shutil
import random
from django.utils.text import slugify
from django.core.files import File

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from products.models import Product, Category, ProductImage

def import_shoes(source_dir):
    print(f"--- Starting Bulk Shoe Import from {source_dir} ---")
    
    # 1. Ensure Footwear Category exists
    category, created = Category.objects.get_or_create(
        name="Footwear",
        defaults={'description': "Premium quality shoes and boots for every occasion."}
    )
    if created:
        print("Created new 'Footwear' category.")

    # 2. Define the shoe data based on your files
    files = [f for f in os.listdir(source_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    
    for filename in files:
        # Clean up name (e.g., "Italian leather shoes.jpg" -> "Italian Leather Shoes")
        raw_name = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()
        
        # Make it sound more premium
        if "Shoes" in raw_name and "Premium" not in raw_name:
            product_name = f"Premium {raw_name}"
        elif "Boots" in raw_name:
            product_name = f"Handcrafted {raw_name}"
        else:
            product_name = raw_name
            
        product_slug = slugify(product_name)
        
        # Check if product already exists to avoid duplicates
        if Product.objects.filter(slug=product_slug).exists():
            print(f"Skipping {product_name} (Already exists)")
            continue
            
        # 3. Create Product
        price = round(random.uniform(45.00, 55.00), 2)
        stock = random.randint(15, 50)
        sku = f"SHOE-{random.randint(1000, 9999)}"
        
        description = f"Experience ultimate comfort and style with our {product_name}. Perfect for both formal and casual settings, these are designed with durability and aesthetics in mind."
        
        product = Product.objects.create(
            name=product_name,
            slug=product_slug,
            description=description,
            category=category,
            price=price,
            stock=stock,
            sku=sku,
            brand="Achol Premium",
            is_active=True,
            is_featured=random.choice([True, False])
        )
        print(f"[OK] Created Product: {product_name} (${price})")

        # 4. Handle Image
        source_path = os.path.join(source_dir, filename)
        with open(source_path, 'rb') as f:
            product_image = ProductImage(
                product=product,
                is_primary=True,
                alt_text=product_name
            )
            # This copies the file to the media/products/ directory
            product_image.image.save(filename, File(f), save=True)
            print(f"  - Image linked: {filename}")

    print("--- Import Complete! ---")

if __name__ == "__main__":
    import_shoes(r"E:\Shoes")
