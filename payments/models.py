from django.db import models
from django.core.validators import MinValueValidator
from core.models import BaseModel
from orders.models import Order


class Payment(BaseModel):
    """Payment model for tracking all payment transactions."""
    
    GATEWAY_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Payment info
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_gateway = models.CharField(max_length=50, choices=GATEWAY_CHOICES, default='stripe')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='USD')
    
    # Transaction info
    transaction_id = models.CharField(max_length=255, unique=True, blank=True)
    reference_number = models.CharField(max_length=255, blank=True)
    
    # Additional info
    notes = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    
    # Refund tracking
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    refund_date = models.DateTimeField(null=True, blank=True)
    refund_reason = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['order']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Payment for Order {self.order.order_number}"

    def can_be_refunded(self):
        """Check if payment can be refunded."""
        return self.status == 'completed'


class PaymentMethod(BaseModel):
    """Payment method model for storing user payment methods."""
    
    METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
        ('bank_account', 'Bank Account'),
        ('mobile_money', 'Mobile Money'),
    ]
    
    # User and method info
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='payment_methods')
    method_type = models.CharField(max_length=50, choices=METHOD_CHOICES)
    is_primary = models.BooleanField(default=False)
    
    # Card info (encrypted in production)
    card_last_four = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=50, blank=True)  # Visa, Mastercard, etc.
    expiry_month = models.IntegerField(blank=True, null=True)
    expiry_year = models.IntegerField(blank=True, null=True)
    
    # Tokenized payment info
    payment_token = models.CharField(max_length=255, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Payment Method'
        verbose_name_plural = 'Payment Methods'
        unique_together = ('user', 'payment_token')

    def __str__(self):
        if self.card_last_four:
            return f"{self.card_brand} ending in {self.card_last_four}"
        return f"{self.method_type} for {self.user.email}"

    def save(self, *args, **kwargs):
        """Ensure only one primary payment method per user."""
        if self.is_primary:
            PaymentMethod.objects.filter(user=self.user).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)
