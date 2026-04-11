from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from products.models import Product
from .models import Cart, CartItem, Order, OrderItem
from .forms import CartItemForm, CheckoutForm
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer, CheckoutSerializer


# ============================================================================
# SHOPPING CART - API VIEWS
# ============================================================================

class CartDetailAPIView(generics.RetrieveUpdateAPIView):
    """API view for cart details and updates."""
    
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart


class AddToCartAPIView(generics.CreateAPIView):
    """API view for adding items to cart."""
    
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        cart, _ = Cart.objects.get_or_create(user=user)
        
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not product.is_in_stock():
            return Response(
                {'error': 'Product out of stock'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if quantity > product.stock:
            return Response(
                {'error': f'Only {product.stock} items available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity, 'price': product.get_display_price()}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        serializer = self.get_serializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartItemDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API view for cart item operations."""
    
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def update(self, request, *args, **kwargs):
        cart_item = self.get_object()
        quantity = request.data.get('quantity')
        
        if quantity is not None:
            if quantity <= 0:
                cart_item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            
            if quantity > cart_item.product.stock:
                return Response(
                    {'error': f'Only {cart_item.product.stock} items available'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cart_item.quantity = quantity
            cart_item.save()
        
        serializer = self.get_serializer(cart_item)
        return Response(serializer.data)


# ============================================================================
# ORDERS - API VIEWS
# ============================================================================

class OrderListAPIView(generics.ListAPIView):
    """API view for listing user orders."""
    
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class OrderDetailAPIView(generics.RetrieveAPIView):
    """API view for order details."""
    
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class CheckoutAPIView(generics.CreateAPIView):
    """API view for checkout process."""
    
    serializer_class = CheckoutSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        
        if not cart.items.exists():
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create order
        order = Order.objects.create(
            user=user,
            subtotal=cart.get_total_price(),
            total_amount=cart.get_total_price(),
            delivery_address=serializer.validated_data['delivery_address'],
            delivery_location=serializer.validated_data['delivery_location'],
            delivery_phone=serializer.validated_data['delivery_phone'],
            notes=serializer.validated_data.get('notes', ''),
        )
        
        # Create order items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                unit_price=cart_item.price,
            )
        
        # Clear cart
        cart.clear()
        
        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)


# ============================================================================
# SHOPPING CART - WEB VIEWS
# ============================================================================

class CartView(TemplateView):
    """Web view for shopping cart page."""
    
    template_name = 'cart/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=self.request.user)
            context['cart'] = cart
            context['cart_items'] = cart.items.all()
            context['total_price'] = cart.get_total_price()
            context['total_discount'] = cart.get_total_discount()
        return context


class AddToCartView(LoginRequiredMixin, TemplateView):
    """Web view for adding product to cart."""
    
    login_url = 'auth:login'
    template_name = 'products/add_to_cart_modal.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = get_object_or_404(Product, slug=self.kwargs['slug'])
        context['product'] = product
        context['form'] = CartItemForm()
        return context

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, slug=self.kwargs['slug'])
        form = CartItemForm(request.POST)
        
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            
            if not product.is_in_stock():
                return JsonResponse({'error': 'Product out of stock'}, status=400)
            
            if quantity > product.stock:
                return JsonResponse({'error': f'Only {product.stock} items available'}, status=400)
            
            cart, _ = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity, 'price': product.get_display_price()}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to cart',
                'cart_count': cart.get_total_items(),
                'redirect_url': '/cart/'
            })
        
        return JsonResponse({'error': 'Invalid quantity'}, status=400)


class RemoveFromCartView(LoginRequiredMixin, TemplateView):
    """Web view for removing item from cart."""
    
    login_url = 'auth:login'

    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()
        return redirect('cart:cart')


class UpdateCartItemView(LoginRequiredMixin, TemplateView):
    """Web view for updating cart item quantity."""
    
    login_url = 'auth:login'

    def post(self, request, item_id):
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = request.POST.get('quantity')
        
        if quantity:
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    cart_item.delete()
                else:
                    cart_item.quantity = quantity
                    cart_item.save()
            except ValueError:
                pass
        
        return redirect('cart:cart')


# ============================================================================
# ORDERS - WEB VIEWS
# ============================================================================

class OrderListView(LoginRequiredMixin, ListView):
    """Web view for listing user orders."""
    
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10
    login_url = 'auth:login'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class OrderDetailView(LoginRequiredMixin, DetailView):
    """Web view for order details."""
    
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    slug_field = 'order_number'
    slug_url_kwarg = 'order_number'
    login_url = 'auth:login'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class CheckoutView(LoginRequiredMixin, TemplateView):
    """Web view for checkout process."""
    
    template_name = 'orders/checkout.html'
    login_url = 'auth:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        cart = get_object_or_404(Cart, user=user)
        
        if not cart.items.exists():
            return redirect('cart:cart')
        
        context['cart'] = cart
        context['form'] = CheckoutForm(initial={
            'delivery_address': user.street_address,
            'delivery_location': user.location,
            'delivery_phone': user.phone_number,
        })
        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        form = CheckoutForm(request.POST)
        
        if form.is_valid():
            # Create order
            order = form.save(commit=False)
            order.user = user
            order.subtotal = cart.get_total_price()
            order.total_amount = cart.get_total_price()
            order.save()
            
            # Create order items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.price,
                )
            
            # Clear cart
            cart.clear()
            
            return redirect('orders:confirmation', order_number=order.order_number)
        
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)


class OrderConfirmationView(LoginRequiredMixin, DetailView):
    """Web view for order confirmation."""
    
    model = Order
    template_name = 'orders/confirmation.html'
    context_object_name = 'order'
    slug_field = 'order_number'
    slug_url_kwarg = 'order_number'
    login_url = 'auth:login'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')
