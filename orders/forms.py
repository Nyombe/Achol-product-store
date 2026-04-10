from django import forms
from .models import Order, Cart


class CartItemForm(forms.Form):
    """Form for adding items to cart."""
    
    quantity = forms.IntegerField(
        min_value=1,
        max_value=1000,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 70px'})
    )


class CheckoutForm(forms.ModelForm):
    """Form for order checkout."""
    
    class Meta:
        model = Order
        fields = (
            'shipping_address', 'shipping_city', 'shipping_state',
            'shipping_postal_code', 'shipping_country', 'shipping_phone', 'notes'
        )
        widgets = {
            'shipping_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address'}),
            'shipping_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'shipping_state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State/Province'}),
            'shipping_postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal code'}),
            'shipping_country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'shipping_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 000-0000'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Order notes (optional)', 'rows': 3}),
        }

    def clean_shipping_phone(self):
        """Validate phone number."""
        import re
        phone = self.cleaned_data.get('shipping_phone')
        if phone and not re.match(r'^\+?1?\d{9,15}$', phone.replace(' ', '').replace('-', '')):
            raise forms.ValidationError('Please enter a valid phone number.')
        return phone
