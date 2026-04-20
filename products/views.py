from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Product, ProductImage, PriceHistory, ProductReview
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ProductImageSerializer, PriceHistorySerializer, ProductReviewSerializer
)
from .forms import ProductReviewForm


# ============================================================================
# API VIEWS
# ============================================================================

class CategoryListAPIView(generics.ListAPIView):
    """API view for listing categories."""
    
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None


class ProductListAPIView(generics.ListAPIView):
    """API view for listing products with filtering and search."""
    
    queryset = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_featured']
    search_fields = ['name', 'description', 'sku', 'brand']
    ordering_fields = ['price', 'created_at', 'rating', '-views']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Price range filtering
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        return queryset


class ProductDetailAPIView(generics.RetrieveAPIView):
    """API view for product details."""
    
    queryset = Product.objects.select_related('category').prefetch_related('images', 'price_history', 'reviews')
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        # Increment view count
        product = self.get_object()
        product.views += 1
        product.save(update_fields=['views'])
        return response


class ProductPriceHistoryAPIView(generics.ListAPIView):
    """API view for product price history."""
    
    serializer_class = PriceHistorySerializer
    permission_classes = [AllowAny]
    ordering = ['-created_at']

    def get_queryset(self):
        product = get_object_or_404(Product, slug=self.kwargs['slug'])
        return product.price_history.all()


# ============================================================================
# WEB VIEWS
# ============================================================================

class ProductListView(ListView):
    """Web view for listing products."""
    
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
        
        # Search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(sku__icontains=search_query)
            )
        
        # Category filter
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Price range filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Sorting
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by in ['price', '-price', 'rating', '-rating', 'created_at', '-created_at']:
            queryset = queryset.order_by(sort_by)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_category'] = self.request.GET.get('category', '')
        return context


class ProductDetailView(DetailView):
    """Web view for product details."""
    
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'price_history', 'reviews')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        product.views += 1
        product.save(update_fields=['views'])
        
        context['price_history'] = product.price_history.all()[:10]
        context['reviews'] = product.reviews.filter(is_approved=True)
        context['related_products'] = product.get_recommendations(limit=6)
        
        return context


class CategoryProductsView(ListView):
    """Web view for products in a specific category."""
    
    model = Product
    template_name = 'products/category_products.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Product.objects.filter(
            category=category,
            is_active=True
        ).select_related('category').prefetch_related('images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category, slug=self.kwargs['slug'])
        return context


class ProductSearchView(ListView):
    """Web view for product search."""
    
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        category_slug = self.request.GET.get('category', '')
        
        queryset = Product.objects.filter(is_active=True)
        
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(sku__icontains=query)
            ).distinct()
            
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
            
        return queryset.select_related('category').prefetch_related('images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_category_slug'] = self.request.GET.get('category', '')
        return context

class AddReviewView(LoginRequiredMixin, View):
    """Web view for an authenticated user to submit a product review"""
    def post(self, request, slug, *args, **kwargs):
        product = get_object_or_404(Product, slug=slug)
        
        # Check if user already reviewed
        if product.reviews.filter(user=request.user).exists():
            messages.error(request, "You have already submitted a review for this product.")
            return redirect('products:product_detail', slug=slug)
            
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Your review has been submitted successfully and is pending approval.")
        else:
            messages.error(request, "There was an error with your review. Please try again.")
            
        return redirect('products:product_detail', slug=slug)
