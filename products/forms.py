from django import forms
from .models import ProductReview

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'title', 'content']
        widgets = {
            'rating': forms.Select(attrs={'class': 'block w-full px-4 py-3 border border-gray-200 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-gray-50'}),
            'title': forms.TextInput(attrs={'class': 'block w-full px-4 py-3 border border-gray-200 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-gray-50', 'placeholder': 'Summarize your review'}),
            'content': forms.Textarea(attrs={'rows': 4, 'class': 'block w-full px-4 py-3 border border-gray-200 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm bg-gray-50', 'placeholder': 'Write your full review here...'}),
        }
