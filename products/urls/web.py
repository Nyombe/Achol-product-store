from django.urls import path
from .. import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('search/', views.ProductSearchView.as_view(), name='search'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('<slug:slug>/review/', views.AddReviewView.as_view(), name='add_review'),
    path('category/<slug:slug>/', views.CategoryProductsView.as_view(), name='category_products'),
]
