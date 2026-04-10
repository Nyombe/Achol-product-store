from django.urls import path
from .. import views

app_name = 'api_orders'

urlpatterns = [
    # Cart endpoints
    path('cart/', views.CartDetailAPIView.as_view(), name='cart_detail'),
    path('cart/add/', views.AddToCartAPIView.as_view(), name='add_to_cart'),
    path('cart/items/<int:item_id>/', views.CartItemDetailAPIView.as_view(), name='cart_item_detail'),
    
    # Order endpoints
    path('', views.OrderListAPIView.as_view(), name='order_list'),
    path('<int:pk>/', views.OrderDetailAPIView.as_view(), name='order_detail'),
    path('checkout/', views.CheckoutAPIView.as_view(), name='checkout'),
]
