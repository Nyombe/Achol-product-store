from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum, Count, Avg, F
from django.utils import timezone
from datetime import timedelta
from orders.models import Order, OrderItem
from products.models import Product, Category
import json
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


class AnalyticsDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'analytics/dashboard.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get date range from request
        days = int(self.request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Base Querysets
        orders = Order.objects.filter(created_at__gte=start_date)
        completed_orders = orders.filter(payment_status='completed')
        
        # KPI Metrics
        total_revenue = completed_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        total_orders = orders.count()  # Inclusive of all statuses
        pending_orders = orders.filter(payment_status='pending').count()
        avg_order_value = completed_orders.aggregate(avg=Avg('total_amount'))['avg'] or 0
        # If no completed orders, show avg based on all orders for visibility
        if avg_order_value == 0 and total_orders > 0:
            avg_order_value = orders.aggregate(avg=Avg('total_amount'))['avg'] or 0
            
        total_products = Product.objects.count()
        
        # Sales Trend Data (Last N days)
        trend_data = []
        labels = []
        for i in range(days, -1, -1):
            date = (timezone.now() - timedelta(days=i)).date()
            day_revenue = completed_orders.filter(created_at__date=date).aggregate(total=Sum('total_amount'))['total'] or 0
            trend_data.append(day_revenue)
            labels.append(date.strftime('%b %d'))
            
        # Top Performing Areas (Locations)
        top_locations = completed_orders.values('delivery_location').annotate(
            total_sales=Sum('total_amount'),
            order_count=Count('id')
        ).order_by('-total_sales')[:10]
        
        # Top Selling Products
        top_products = OrderItem.objects.filter(order__in=completed_orders).values(
            'product__name'
        ).annotate(
            total_qty=Sum('quantity'),
            total_revenue=Sum(F('quantity') * F('unit_price'))
        ).order_by('-total_qty')[:5]
        
        # Category Distribution
        category_data = OrderItem.objects.filter(order__in=completed_orders).values(
            'product__category__name'
        ).annotate(
            total_sales=Sum(F('quantity') * F('unit_price'))
        ).order_by('-total_sales')

        # Formatting data for Chart.js
        context.update({
            'kpis': {
                'revenue': total_revenue,
                'orders': total_orders,
                'pending': pending_orders,
                'aov': avg_order_value,
                'products': total_products,
            },
            'labels': json.dumps(labels),
            'trend_data': json.dumps(trend_data, cls=DecimalEncoder),
            'location_labels': json.dumps([loc['delivery_location'] or 'Unknown' for loc in top_locations]),
            'location_data': json.dumps([loc['total_sales'] for loc in top_locations], cls=DecimalEncoder),
            'product_labels': json.dumps([p['product__name'] for p in top_products]),
            'product_data': json.dumps([p['total_qty'] for p in top_products]),
            'category_labels': json.dumps([c['product__category__name'] for c in category_data]),
            'category_data': json.dumps([c['total_sales'] for c in category_data], cls=DecimalEncoder),
            'recent_orders': Order.objects.all()[:5],
            'selected_days': days,
        })
        
        return context
