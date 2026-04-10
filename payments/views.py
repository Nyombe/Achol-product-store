from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

from orders.models import Order
from .models import Payment, PaymentMethod
from .serializers import PaymentSerializer, PaymentMethodSerializer
from .services import PaymentService


class ProcessPaymentAPIView(APIView):
    """API view for processing payments."""
    
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Process a payment for an order."""
        order_id = request.data.get('order_id')
        payment_method = request.data.get('payment_method')
        
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Initialize payment service
        payment_service = PaymentService(gateway='stripe')
        
        # Process payment
        payment = payment_service.process_payment(
            order=order,
            amount=float(order.total_amount),
            payment_method=payment_method
        )
        
        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED if payment.status == 'completed' else status.HTTP_400_BAD_REQUEST)


class PaymentMethodListAPIView(generics.ListCreateAPIView):
    """API view for listing and creating payment methods."""
    
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user, is_active=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PaymentMethodDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API view for managing individual payment methods."""
    
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)


class RefundPaymentAPIView(APIView):
    """API view for refunding a payment."""
    
    permission_classes = [IsAuthenticated]

    def post(self, request, payment_id):
        """Refund a payment."""
        payment = get_object_or_404(Payment, id=payment_id, order__user=request.user)
        
        payment_service = PaymentService(gateway=payment.payment_gateway)
        success = payment_service.refund_payment(payment)
        
        if success:
            return Response(
                {'message': 'Payment refunded successfully'},
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'error': 'Failed to refund payment'},
            status=status.HTTP_400_BAD_REQUEST
        )


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """Webhook view for Stripe payment events."""
    
    def post(self, request):
        """Handle Stripe webhook events."""
        payload = request.body
        signature = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        payment_service = PaymentService(gateway='stripe')
        event = payment_service.verify_webhook(payload, signature)
        
        if not event:
            return JsonResponse({'error': 'Invalid signature'}, status=400)
        
        # Handle different event types
        if event['type'] == 'payment_intent.succeeded':
            intent = event['data']['object']
            order_id = intent['metadata'].get('order_id')
            if order_id:
                try:
                    payment = Payment.objects.get(transaction_id=intent['id'])
                    payment.status = 'completed'
                    payment.save()
                    
                    order = Order.objects.get(id=order_id)
                    order.payment_status = 'completed'
                    order.status = 'confirmed'
                    order.save()
                except (Payment.DoesNotExist, Order.DoesNotExist):
                    pass
        
        elif event['type'] == 'payment_intent.payment_failed':
            intent = event['data']['object']
            try:
                payment = Payment.objects.get(transaction_id=intent['id'])
                payment.status = 'failed'
                payment.save()
            except Payment.DoesNotExist:
                pass
        
        return JsonResponse({'status': 'success'})
