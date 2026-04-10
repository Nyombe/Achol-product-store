from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem, Order, OrderItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'total_price_display')
    list_filter = ('is_active',)
    search_fields = ('user__email',)

    def total_price_display(self, obj):
        return f'₦{obj.get_total_price()}'
    total_price_display.short_description = 'Total'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'price')
    search_fields = ('product__name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status_badge', 'payment_status_badge', 'total_amount', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'user__email')

    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'confirmed': '#4169E1',
            'processing': '#9370DB',
            'shipped': '#32CD32',
            'delivered': '#228B22',
            'cancelled': '#DC143C',
            'refunded': '#FF6347',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#808080'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Order Status'

    def payment_status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'completed': '#228B22',
            'failed': '#DC143C',
            'refunded': '#FF6347',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.payment_status, '#808080'),
            obj.get_payment_status_display()
        )
    payment_status_badge.short_description = 'Payment'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'unit_price', 'total_display')
    search_fields = ('order__order_number', 'product__name')

    def total_display(self, obj):
        return f'₦{obj.get_total_price()}'
    total_display.short_description = 'Total'
