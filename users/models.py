from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from core.models import TimeStampedModel


class CustomUser(AbstractUser):
    """Extended user model with additional fields."""
    
    # Additional fields
    phone_number = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Address fields
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Account status
    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Override related names to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='customuser_set',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='customuser_set',
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_address(self):
        """Return formatted full address."""
        address_parts = [
            self.street_address,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ', '.join([part for part in address_parts if part])

    def clean(self):
        """Validate user data."""
        super().clean()
        if self.email and CustomUser.objects.filter(
            email=self.email
        ).exclude(pk=self.pk).exists():
            raise ValidationError({'email': 'This email is already in use.'})
        if self.phone_number and len(self.phone_number) < 10:
            raise ValidationError({'phone_number': 'Phone number must be at least 10 digits.'})


class UserPreferences(TimeStampedModel):
    """User preferences and settings."""
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='preferences')
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    order_updates = models.BooleanField(default=True)
    promotional_emails = models.BooleanField(default=True)
    
    # Privacy
    show_profile = models.BooleanField(default=False)
    allow_data_collection = models.BooleanField(default=False)
    
    # Preferences
    preferred_currency = models.CharField(max_length=3, default='USD')
    preferred_language = models.CharField(max_length=10, default='en')
    theme = models.CharField(
        max_length=20,
        choices=[('light', 'Light'), ('dark', 'Dark')],
        default='light'
    )

    class Meta:
        verbose_name = 'User Preference'
        verbose_name_plural = 'User Preferences'

    def __str__(self):
        return f"Preferences for {self.user.email}"
