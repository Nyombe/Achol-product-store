from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from core.models import BaseModel
from products.models import Product

User = get_user_model()


class Cart(BaseModel):
    """Shopping cart model."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        return f"Cart for {self.user.email}"

    def get_total_price(self):
        """Calculate total price of all items in cart."""
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_items(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.all())

    def get_total_discount(self):
        """Calculate total discount from all items."""
        return sum(item.get_discount_amount() for item in self.items.all())

    def clear(self):
        """Clear all items from cart."""
        self.items.all().delete()

    def clean(self):
        """Validate cart data."""
        super().clean()
        # Ensure all items are still in stock
        for item in self.items.all():
            if not item.product.is_in_stock():
                raise ValidationError(f'{item.product.name} is out of stock.')


class CartItem(BaseModel):
    """Individual item in shopping cart."""
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Snapshot of price at time of adding

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ('cart', 'product')
        indexes = [
            models.Index(fields=['cart']),
        ]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_total_price(self):
        """Get total price for this item."""
        return self.price * self.quantity

    def get_discount_amount(self):
        """Get discount amount for this item."""
        if self.product.discount_price:
            discount_per_unit = self.product.price - self.product.discount_price
            return discount_per_unit * self.quantity
        return 0

    def clean(self):
        """Validate cart item."""
        super().clean()
        if self.quantity > self.product.stock:
            raise ValidationError(f'Only {self.product.stock} items available.')

    def save(self, *args, **kwargs):
        """Save and update cart item."""
        if not self.price:
            self.price = self.product.get_display_price()
        self.full_clean()
        super().save(*args, **kwargs)


class Order(BaseModel):
    """Order model."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    # User info
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders')
    
    # Order details
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Shipping info
    shipping_address = models.CharField(max_length=500)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100)
    shipping_phone = models.CharField(max_length=20)
    
    # Additional info
    notes = models.TextField(blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        """Generate order number if not set."""
        if not self.order_number:
            import uuid
            self.order_number = f"ORD-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    def get_shipping_address(self):
        """Get formatted shipping address."""
        address_parts = [
            self.shipping_address,
            self.shipping_city,
            self.shipping_state,
            self.shipping_postal_code,
            self.shipping_country,
        ]
        return ', '.join([part for part in address_parts if part])

    def can_be_cancelled(self):
        """Check if order can be cancelled."""
        return self.status in ['pending', 'confirmed']

    def can_be_shipped(self):
        """Check if order can be shipped."""
        return self.status == 'processing'


class OrderItem(BaseModel):
    """Individual item in an order."""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.product.name if self.product else 'Deleted Product'} x {self.quantity}"

    def get_total_price(self):
        """Get total price for this order item."""
        return (self.unit_price * self.quantity) - self.discount

    def get_subtotal(self):
        """Get subtotal before discount."""
        return self.unit_price * self.quantity
