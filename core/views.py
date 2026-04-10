from django.views.generic import TemplateView
from django.shortcuts import render
from products.models import Category, Product


class HomePageView(TemplateView):
    """Homepage view."""
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.filter(
            is_active=True
        ).select_related('category')[:12]
        context['categories'] = Category.objects.filter(is_active=True)[:6]
        return context

class AboutView(TemplateView):
    template_name = 'core/about.html'

class ContactView(TemplateView):
    template_name = 'core/contact.html'
