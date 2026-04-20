from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from .models import Category, Product, ProductImage, PriceHistory, ProductReview

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image_preview', 'image', 'image_url', 'alt_text', 'is_primary', 'order')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-width: 80px; max-height: 80px; object-fit: cover; border-radius: 8px;" />')
        return ""
    image_preview.short_description = 'Preview'



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'product_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')

    def product_count(self, obj):
        count = obj.products.count()
        return format_html('<b>{}</b>', count)
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'styled_price', 'stock_display', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'sku')

    inlines = [ProductImageInline]

    def styled_price(self, obj):
        if obj.discount_price:
            return mark_safe(
                f'<div style="display: flex; flex-direction: column; align-items: flex-start;">'
                f'<span style="color: #ff3c3c; font-weight: bold; font-size: 1.2em; background: #fff0f0; border-radius: 8px; padding: 2px 8px; margin-bottom: 2px; display: inline-block;">US${obj.discount_price:.2f}</span>'
                f'<span style="text-decoration: line-through; color: #888; font-size: 0.95em;">US${obj.price:.2f}</span>'
                f'</div>'
            )
        return mark_safe(
            f'<span style="color: #ff3c3c; font-weight: bold; font-size: 1.2em; background: #fff0f0; border-radius: 8px; padding: 2px 8px;">US${obj.price:.2f}</span>'
        )
    styled_price.short_description = 'Price'

    def stock_display(self, obj):
        if obj.stock <= 0:
            return mark_safe('<span style="color: red;">Out of Stock</span>')
        elif obj.stock < obj.low_stock_threshold:
            return format_html('<span style="color: orange;">Low ({} left)</span>', obj.stock)
        return mark_safe('<span style="color: green;">In Stock</span>')
    stock_display.short_description = 'Stock'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_primary', 'order')
    list_filter = ('is_primary',)
    search_fields = ('product__name',)


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'old_price', 'new_price', 'change_reason', 'created_at')
    list_filter = ('change_reason',)
    search_fields = ('product__name', 'product__sku')
    readonly_fields = ('created_at',)


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'rating', 'title', 'is_approved')
    list_filter = ('rating', 'is_approved')
    search_fields = ('product__name', 'title')
