from django.urls import path
from .. import views

app_name = 'api_products'

urlpatterns = [
    path('', views.ProductListAPIView.as_view(), name='product_list'),
    path('<slug:slug>/', views.ProductDetailAPIView.as_view(), name='product_detail'),
    path('<slug:slug>/price-history/', views.ProductPriceHistoryAPIView.as_view(), name='price_history'),
    path('categories/', views.CategoryListAPIView.as_view(), name='category_list'),
]
