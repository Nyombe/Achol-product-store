from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, UserPreferences
import re


class CustomUserCreationForm(UserCreationForm):
    """Form for user registration with enhanced validation."""
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    phone_number = forms.CharField(max_length=20, required=False)

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'password1', 'password2')

    def clean_email(self):
        """Validate email uniqueness."""
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_password1(self):
        """Validate password strength."""
        password = self.cleaned_data.get('password1')
        
        if len(password) < 8:
            raise forms.ValidationError('Password must be at least 8 characters long.')
        
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError('Password must contain at least one uppercase letter.')
        
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError('Password must contain at least one lowercase letter.')
        
        if not re.search(r'[0-9]', password):
            raise forms.ValidationError('Password must contain at least one digit.')
        
        return password

    def clean_phone_number(self):
        """Validate phone number format."""
        phone = self.cleaned_data.get('phone_number')
        if phone and not re.match(r'^\+?1?\d{9,15}$', phone.replace(' ', '').replace('-', '')):
            raise forms.ValidationError('Please enter a valid phone number.')
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # Use email as username
        if commit:
            user.save()
            # Create user preferences
            UserPreferences.objects.get_or_create(user=user)
        return user


class CustomUserChangeForm(UserChangeForm):
    """Form for updating user profile."""
    
    class Meta:
        model = CustomUser
        fields = (
            'first_name', 'last_name', 'phone_number', 'date_of_birth',
            'street_address', 'city', 'state', 'postal_code', 'country'
        )
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'street_address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }


class UserPreferencesForm(forms.ModelForm):
    """Form for user preferences."""
    
    class Meta:
        model = UserPreferences
        fields = (
            'email_notifications', 'sms_notifications', 'order_updates',
            'promotional_emails', 'show_profile', 'allow_data_collection',
            'preferred_currency', 'preferred_language', 'theme'
        )
        widgets = {
            'email_notifications': forms.CheckboxInput(),
            'sms_notifications': forms.CheckboxInput(),
            'order_updates': forms.CheckboxInput(),
            'promotional_emails': forms.CheckboxInput(),
            'show_profile': forms.CheckboxInput(),
            'allow_data_collection': forms.CheckboxInput(),
        }
