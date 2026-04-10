from django.contrib import admin
from django.utils.html import format_html
from .models import Payment, PaymentMethod


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount_display', 'status_badge', 'payment_gateway', 'created_at')
    list_filter = ('payment_gateway', 'status', 'created_at')
    search_fields = ('order__order_number', 'transaction_id')

    def amount_display(self, obj):
        return f'₦{obj.amount}'
    amount_display.short_description = 'Amount'

    def status_badge(self, obj):
        colors = {
            'pending': '#FFA500',
            'completed': '#228B22',
            'failed': '#DC143C',
            'refunded': '#4169E1',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#808080'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'method_type', 'is_primary_badge', 'is_active_badge')
    list_filter = ('method_type', 'is_primary', 'is_active')
    search_fields = ('user__email',)

    def is_primary_badge(self, obj):
        if obj.is_primary:
            return format_html('<span style="color: green;">★ Primary</span>')
        return '-'
    is_primary_badge.short_description = 'Primary'

    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Active</span>')
        return format_html('<span style="color: gray;">✗ Inactive</span>')
    is_active_badge.short_description = 'Status'
