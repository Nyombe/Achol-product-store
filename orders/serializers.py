from rest_framework import serializers
from orders.models import Cart, CartItem, Order, OrderItem
from products.serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem model."""
    
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.SerializerMethodField()
    discount_amount = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'price', 'total_price', 'discount_amount', 'created_at')
        read_only_fields = ('id', 'price', 'created_at')

    def get_total_price(self, obj):
        return str(obj.get_total_price())

    def get_discount_amount(self, obj):
        return str(obj.get_discount_amount())


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model."""
    
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    total_discount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'total_items', 'total_price', 'total_discount', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def get_total_price(self, obj):
        return str(obj.get_total_price())

    def get_total_items(self, obj):
        return obj.get_total_items()

    def get_total_discount(self, obj):
        return str(obj.get_total_discount())


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model."""
    
    product_name = serializers.CharField(source='product.name', read_only=True, allow_null=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True, allow_null=True)
    total_price = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'product_sku', 'quantity', 'unit_price', 'discount', 'subtotal', 'total_price', 'created_at')
        read_only_fields = ('id', 'created_at')

    def get_total_price(self, obj):
        return str(obj.get_total_price())

    def get_subtotal(self, obj):
        return str(obj.get_subtotal())


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model."""
    
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True, allow_null=True)
    delivery_address_full = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'user', 'user_email', 'status', 'payment_status',
            'subtotal', 'tax_amount', 'shipping_cost', 'discount_amount', 'total_amount',
            'delivery_address_full', 'delivery_phone', 'tracking_number', 'items',
            'notes', 'delivered_at', 'cancelled_at', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'order_number', 'user', 'delivered_at', 'cancelled_at', 'created_at', 'updated_at'
        )

    def get_delivery_address_full(self, obj):
        return obj.get_delivery_address()


class CheckoutSerializer(serializers.Serializer):
    """Serializer for checkout process."""
    
    delivery_address = serializers.CharField(max_length=500)
    delivery_location = serializers.CharField(max_length=100)
    delivery_phone = serializers.CharField(max_length=20)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_delivery_phone(self, value):
        import re
        if not re.match(r'^\+?1?\d{9,15}$', value.replace(' ', '').replace('-', '')):
            raise serializers.ValidationError('Invalid phone number.')
        return value
