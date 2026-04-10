from django.urls import path
from payments import views

app_name = 'api_payments'

urlpatterns = [
    path('process/', views.ProcessPaymentAPIView.as_view(), name='process_payment'),
    path('methods/', views.PaymentMethodListAPIView.as_view(), name='payment_methods'),
    path('methods/<int:pk>/', views.PaymentMethodDetailAPIView.as_view(), name='payment_method_detail'),
    path('<int:payment_id>/refund/', views.RefundPaymentAPIView.as_view(), name='refund_payment'),
    path('webhook/stripe/', views.StripeWebhookView.as_view(), name='stripe_webhook'),
]
