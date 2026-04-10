from rest_framework import serializers
from products.models import Category, Product, ProductImage, PriceHistory, ProductReview


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'image', 'products_count', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at')

    def get_products_count(self, obj):
        return obj.products.filter(is_active=True).count()


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for ProductImage model."""
    
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'alt_text', 'is_primary', 'order')


class PriceHistorySerializer(serializers.ModelSerializer):
    """Serializer for PriceHistory model."""
    
    price_change = serializers.SerializerMethodField()
    price_change_percentage = serializers.SerializerMethodField()

    class Meta:
        model = PriceHistory
        fields = (
            'id', 'product', 'old_price', 'new_price', 'price_change',
            'price_change_percentage', 'change_reason', 'notes', 'created_at'
        )
        read_only_fields = ('id', 'created_at')

    def get_price_change(self, obj):
        return str(obj.get_price_change())

    def get_price_change_percentage(self, obj):
        return obj.get_price_change_percentage()


class ProductReviewSerializer(serializers.ModelSerializer):
    """Serializer for ProductReview model."""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = ProductReview
        fields = ('id', 'user', 'user_name', 'rating', 'title', 'content', 'is_verified_purchase', 'helpful_count', 'created_at')
        read_only_fields = ('id', 'user', 'helpful_count', 'created_at')


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for Product list view."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    display_price = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'price', 'discount_price', 'display_price',
            'discount_percentage', 'category', 'category_name', 'primary_image',
            'rating', 'num_ratings', 'stock', 'in_stock', 'is_featured', 'created_at'
        )
        read_only_fields = ('id', 'created_at')

    def get_display_price(self, obj):
        return str(obj.get_display_price())

    def get_discount_percentage(self, obj):
        return obj.get_discount_percentage()

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        return None

    def get_in_stock(self, obj):
        return obj.is_in_stock()


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for Product detail view."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    price_history = PriceHistorySerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    display_price = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    is_low_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'description', 'price', 'discount_price','display_price',
            'discount_percentage', 'category', 'category_name', 'sku', 'brand',
            'stock', 'in_stock', 'is_low_stock', 'weight', 'dimensions',
            'rating', 'num_ratings', 'is_featured', 'images', 'price_history',
            'reviews', 'meta_description', 'meta_keywords', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_display_price(self, obj):
        return str(obj.get_display_price())

    def get_discount_percentage(self, obj):
        return obj.get_discount_percentage()

    def get_in_stock(self, obj):
        return obj.is_in_stock()

    def get_is_low_stock(self, obj):
        return obj.is_low_stock()
