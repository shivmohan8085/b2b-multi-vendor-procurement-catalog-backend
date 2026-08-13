"""Serializers for catalog management."""

from rest_framework import serializers
from apps.catalog.models import Category, Tag, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'is_active']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'sort_order']
        read_only_fields = ['id']


class ProductListSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.company_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'sku', 'short_description', 'price', 'compare_at_price', 'stock_quantity', 'status', 'is_featured', 'vendor_name', 'category_name', 'primary_image', 'created_at']
    
    def get_primary_image(self, obj):
        image = obj.images.filter(is_primary=True).first() or obj.images.first()
        if image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(image.image.url)
            return image.image.url
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.company_name', read_only=True)
    vendor_id = serializers.IntegerField(source='vendor.id', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_id = serializers.IntegerField(source='category.id', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'vendor', 'vendor_id', 'vendor_name', 'category', 'category_id', 'category_name', 'tags', 'name', 'slug', 'sku', 'description', 'short_description', 'price', 'compare_at_price', 'cost_price', 'stock_quantity', 'low_stock_threshold', 'weight', 'dimensions', 'status', 'is_featured', 'min_order_quantity', 'max_order_quantity', 'images', 'is_low_stock', 'is_in_stock', 'created_at', 'updated_at']
        read_only_fields = ['id', 'vendor', 'is_low_stock', 'is_in_stock', 'created_at', 'updated_at']


class ProductCreateSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)
    tag_ids = serializers.ListField(child=serializers.IntegerField(), required=False, write_only=True)
    
    class Meta:
        model = Product
        fields = ['category', 'name', 'slug', 'sku', 'description', 'short_description', 'price', 'compare_at_price', 'cost_price', 'stock_quantity', 'low_stock_threshold', 'weight', 'dimensions', 'status', 'is_featured', 'min_order_quantity', 'max_order_quantity', 'images', 'tag_ids']
    
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        tag_ids = validated_data.pop('tag_ids', [])
        
        product = Product.objects.create(**validated_data)
        
        if tag_ids:
            product.tags.set(tag_ids)
        
        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)
        
        return product


class ProductUpdateSerializer(serializers.ModelSerializer):
    tag_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    
    class Meta:
        model = Product
        fields = ['category', 'name', 'slug', 'sku', 'description', 'short_description', 'price', 'compare_at_price', 'cost_price', 'stock_quantity', 'low_stock_threshold', 'weight', 'dimensions', 'status', 'is_featured', 'min_order_quantity', 'max_order_quantity', 'tag_ids']
    
    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        
        if tag_ids is not None:
            instance.tags.set(tag_ids)
            validated_data.pop('tag_ids', None)
        
        return super().update(instance, validated_data)