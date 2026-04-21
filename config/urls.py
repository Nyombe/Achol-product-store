"""
URL configuration for ecommerce project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('management/', admin.site.urls),
    path('api/auth/', include('users.urls.api')),
    path('api/products/', include('products.urls.api')),
    path('api/orders/', include('orders.urls.api')),
    path('api/payments/', include('payments.urls')),
    path('auth/', include('users.urls.web')),
    path('products/', include('products.urls.web')),
    path('cart/', include('orders.urls.cart')),
    path('orders/', include('orders.urls.web')),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
