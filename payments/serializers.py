from rest_framework import serializers
from .models import Payment, PaymentMethod


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""
    
    order_number = serializers.CharField(source='order.order_number', read_only=True)

    class Meta:
        model = Payment
        fields = (
            'id', 'order', 'order_number', 'payment_gateway', 'status',
            'amount', 'currency', 'transaction_id', 'reference_number',
            'refunded_amount', 'refund_date', 'error_message', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for PaymentMethod model."""
    
    class Meta:
        model = PaymentMethod
        fields = (
            'id', 'method_type', 'is_primary', 'card_last_four',
            'card_brand', 'expiry_month', 'expiry_year', 'is_active', 'created_at'
        )
        read_only_fields = ('id', 'created_at')
        extra_kwargs = {
            'payment_token': {'write_only': True}
        }
