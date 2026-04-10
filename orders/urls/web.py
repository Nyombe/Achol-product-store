from django.urls import path
from .. import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order_list'),
    path('<str:order_number>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('confirmation/<str:order_number>/', views.OrderConfirmationView.as_view(), name='confirmation'),
]
