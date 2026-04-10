"""
Payment service abstraction layer for handling different payment gateways.
Designed for easy integration of multiple payment providers.
"""

import stripe
from django.conf import settings
from django.db import transaction
from .models import Payment


class PaymentGatewayBase:
    """Base class for payment gateways."""
    
    def __init__(self):
        pass

    def process_payment(self, order, amount, payment_method=None):
        """Process a payment. Must be implemented by subclasses."""
        raise NotImplementedError

    def refund_payment(self, payment):
        """Refund a payment. Must be implemented by subclasses."""
        raise NotImplementedError

    def verify_webhook(self, payload, signature):
        """Verify webhook signature. Must be implemented by subclasses."""
        raise NotImplementedError


class StripePaymentGateway(PaymentGatewayBase):
    """Stripe payment gateway implementation."""
    
    def __init__(self):
        super().__init__()
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def process_payment(self, order, amount, payment_method=None):
        """
        Process payment with Stripe.
        
        Args:
            order: Order instance
            amount: Payment amount in dollars
            payment_method: Stripe payment method ID or token
            
        Returns:
            Payment instance
        """
        try:
            with transaction.atomic():
                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    payment_gateway='stripe',
                    amount=amount,
                    status='processing'
                )
                
                # Create Stripe payment intent
                intent = stripe.PaymentIntent.create(
                    amount=int(amount * 100),  # Stripe uses cents
                    currency='usd',
                    payment_method=payment_method,
                    confirm=True,
                    metadata={
                        'order_id': order.id,
                        'order_number': order.order_number,
                    }
                )
                
                # Update payment with transaction details
                payment.transaction_id = intent.id
                payment.reference_number = intent.client_secret
                
                # Update payment status based on intent status
                if intent.status == 'succeeded':
                    payment.status = 'completed'
                    order.payment_status = 'completed'
                    order.status = 'confirmed'
                elif intent.status == 'processing':
                    payment.status = 'processing'
                elif intent.status in ['requires_action', 'requires_payment_method']:
                    payment.status = 'pending'
                else:
                    payment.status = 'failed'
                    payment.error_message = intent.last_payment_error.message if intent.last_payment_error else 'Unknown error'
                
                payment.save()
                order.save()
                
                return payment
        
        except stripe.error.CardError as e:
            # Card error
            payment = Payment.objects.create(
                order=order,
                payment_gateway='stripe',
                amount=amount,
                status='failed',
                error_message=str(e)
            )
            return payment
        
        except stripe.error.StripeError as e:
            # Stripe API error
            payment = Payment.objects.create(
                order=order,
                payment_gateway='stripe',
                amount=amount,
                status='failed',
                error_message=str(e)
            )
            return payment

    def refund_payment(self, payment):
        """
        Refund a Stripe payment.
        
        Args:
            payment: Payment instance to refund
            
        Returns:
            boolean: True if refund successful, False otherwise
        """
        if not payment.can_be_refunded():
            return False
        
        try:
            refund = stripe.Refund.create(
                payment_intent=payment.transaction_id,
                amount=int(payment.amount * 100)
            )
            
            if refund.status == 'succeeded':
                payment.status = 'refunded'
                payment.refunded_amount = payment.amount
                payment.save()
                payment.order.payment_status = 'refunded'
                payment.order.save()
                return True
            
            return False
        
        except stripe.error.StripeError as e:
            payment.error_message = str(e)
            payment.save()
            return False

    def verify_webhook(self, payload, signature):
        """
        Verify Stripe webhook signature.
        
        Args:
            payload: Raw webhook payload
            signature: Stripe signature header
            
        Returns:
            dict: Webhook event data if valid, None otherwise
        """
        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except (ValueError, stripe.error.SignatureVerificationError):
            return None


class PaymentService:
    """
    Service class for handling payments.
    Provides a unified interface for different payment gateways.
    """
    
    def __init__(self, gateway='stripe'):
        """Initialize payment service with specified gateway."""
        if gateway == 'stripe':
            self.gateway = StripePaymentGateway()
        elif gateway == 'paypal':
            # Future: Implement PayPal gateway
            raise NotImplementedError('PayPal gateway not yet implemented')
        elif gateway == 'mobile_money':
            # Future: Implement Mobile Money gateway
            raise NotImplementedError('Mobile Money gateway not yet implemented')
        else:
            raise ValueError(f'Unknown payment gateway: {gateway}')

    def process_payment(self, order, amount, payment_method=None):
        """Process payment using the configured gateway."""
        return self.gateway.process_payment(order, amount, payment_method)

    def refund_payment(self, payment):
        """Refund a payment using the configured gateway."""
        return self.gateway.refund_payment(payment)

    def verify_webhook(self, payload, signature):
        """Verify webhook using the configured gateway."""
        return self.gateway.verify_webhook(payload, signature)
