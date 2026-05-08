"""
Core app admin configuration.
"""
from django.contrib import admin

# Customize the default admin site
admin.site.site_header = "Achol Fashion Store Management"
admin.site.site_title = "Achol Management"
admin.site.index_title = "Welcome to the Achol Admin Portal"

# Dashboard overview counts
_original_index = admin.site.index

def _custom_admin_index(request, extra_context=None):
    from users.models import CustomUser
    from products.models import Product
    from orders.models import Order
    from payments.models import Payment

    extra_context = extra_context or {}
    extra_context.setdefault('dashboard_counts', {
        'users': {'count': CustomUser.objects.count()},
        'products': {'count': Product.objects.filter(is_active=True).count()},
        'orders': {'count': Order.objects.count()},
        'payments': {'count': Payment.objects.count()},
    })
    return _original_index(request, extra_context)

admin.site.index = _custom_admin_index
admin.site.index_template = 'admin/jazzmin/dashboard.html'



