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
            'delivery_address', 'delivery_location', 'delivery_phone', 'notes'
        )
        widgets = {
            'delivery_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address'}),
            'delivery_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Neighborhood / Area'}),
            'delivery_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 000-0000'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Order notes (optional)', 'rows': 3}),
        }

    def clean_delivery_phone(self):
        """Validate phone number."""
        import re
        phone = self.cleaned_data.get('delivery_phone')
        if phone and not re.match(r'^\+?1?\d{9,15}$', phone.replace(' ', '').replace('-', '')):
            raise forms.ValidationError('Please enter a valid phone number.')
        return phone
