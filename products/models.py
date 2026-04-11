from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import BaseModel


class Category(BaseModel):
    """Product category model."""
    
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='subcategories'
    )
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(BaseModel):
    """Product model with comprehensive fields for e-commerce."""
    
    # Basic info
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text='Leave empty if no discount'
    )
    
    # Stock management
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    low_stock_threshold = models.IntegerField(default=10)
    
    # Product details
    sku = models.CharField(max_length=100, unique=True)
    brand = models.CharField(max_length=200, blank=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    dimensions = models.CharField(max_length=255, blank=True)
    
    # Ratings
    rating = models.FloatField(default=0.0, validators=[MinValueValidator(0), ])
    num_ratings = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Tracking
    views = models.IntegerField(default=0)
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    def clean(self):
        """Validate product data."""
        super().clean()
        
        if self.discount_price and self.discount_price >= self.price:
            raise ValidationError({
                'discount_price': 'Discount price must be less than regular price.'
            })

        if self.stock < 0:
            raise ValidationError({'stock': 'Stock cannot be negative.'})

    def get_display_price(self):
        """Get the price to display (discount price if available)."""
        return self.discount_price if self.discount_price else self.price

    def get_discount_percentage(self):
        """Calculate discount percentage."""
        if self.discount_price and self.price:
            discount = ((self.price - self.discount_price) / self.price) * 100
            return round(discount, 2)
        return 0

    def is_in_stock(self):
        """Check if product is in stock."""
        return self.stock > 0

    def is_low_stock(self):
        """Check if product is running low on stock."""
        return self.stock > 0 and self.stock <= self.low_stock_threshold

    def update_rating(self, new_rating, user_id=None):
        """Update product rating."""
        if 0 <= new_rating <= 5:
            avg_rating = ((self.rating * self.num_ratings) + new_rating) / (self.num_ratings + 1)
            self.rating = round(avg_rating, 2)
            self.num_ratings += 1
            self.save()

    def get_recommendations(self, limit=6):
        """
        Get recommended products based on collaborative filtering (co-purchases).
        Falls back to category-based recommendations if not enough purchase data.
        """
        from orders.models import OrderItem
        from django.db.models import Count
        
        # Find order IDs that contain this product
        order_ids = OrderItem.objects.filter(product=self).values_list('order_id', flat=True)
        
        # Find other products in those same orders, ordered by frequency
        recommended = Product.objects.filter(
            order_items__order_id__in=order_ids,
            is_active=True
        ).exclude(
            id=self.id
        ).annotate(
            purchase_count=Count('id')
        ).order_by('-purchase_count')[:limit]
        
        # Convert to list to work with it safely and efficiently
        recommended_list = list(recommended)
        
        # If we don't have enough recommendations, pad with products from the same category
        if len(recommended_list) < limit:
            needed = limit - len(recommended_list)
            recommended_ids = [p.id for p in recommended_list] + [self.id]
            
            fallback = Product.objects.filter(
                category=self.category,
                is_active=True
            ).exclude(
                id__in=recommended_ids
            ).order_by('-views', '-rating')[:needed]
            
            recommended_list.extend(list(fallback))
            
        return recommended_list


class ProductImage(BaseModel):
    """Product image model for multiple images per product."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/', blank=True, null=True, max_length=255)
    image_url = models.URLField(max_length=500, blank=True, help_text='Optional: Use if not uploading an image file.')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    def clean(self):
        super().clean()
        # Ensure either image or image_url is provided
        if not self.image and not self.image_url:
            raise ValidationError('Either an image file or image URL must be provided.')
        # Limit image file size (e.g., 2MB)
        if self.image and self.image.size > 2 * 1024 * 1024:
            raise ValidationError('Image file too large (max 2MB).')

    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(product=self.product).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class PriceHistory(BaseModel):
    """Track price changes for products over time."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    change_reason = models.CharField(
        max_length=255,
        blank=True,
        choices=[
            ('promotion', 'Promotion'),
            ('discount', 'Discount'),
            ('price_adjustment', 'Price Adjustment'),
            ('market_change', 'Market Change'),
            ('sales_event', 'Sales Event'),
            ('other', 'Other'),
        ]
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Price History'
        verbose_name_plural = 'Price Histories'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', '-created_at']),
        ]

    def __str__(self):
        return f"{self.product.name}: {self.old_price} → {self.new_price}"

    def get_price_change(self):
        """Get the price change amount."""
        return self.new_price - self.old_price

    def get_price_change_percentage(self):
        """Get the percentage change."""
        if self.old_price != 0:
            change = ((self.new_price - self.old_price) / self.old_price) * 100
            return round(change, 2)
        return 0


class ProductReview(BaseModel):
    """Customer reviews for products."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='product_reviews')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)
    is_approved = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Product Review'
        verbose_name_plural = 'Product Reviews'
        ordering = ['-created_at']
        unique_together = ('product', 'user')  # One review per user per product
        indexes = [
            models.Index(fields=['product', 'is_approved']),
        ]

    def __str__(self):
        return f"Review of {self.product.name} by {self.user.email}"


# ============================================================================
# SIGNALS
# ============================================================================

@receiver(post_save, sender=Product)
def track_price_change(sender, instance, created, **kwargs):
    """Signal to track price changes in history."""
    if created:
        # Create initial price history record
        PriceHistory.objects.create(
            product=instance,
            old_price=instance.price,
            new_price=instance.price,
            change_reason='initial',
            notes='Product created'
        )
