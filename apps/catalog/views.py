"""Views for catalog management."""

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Category, Tag, Product, ProductImage
from apps.catalog.serializers import (
    CategorySerializer, TagSerializer, ProductListSerializer,
    ProductDetailSerializer, ProductCreateSerializer,
    ProductUpdateSerializer, ProductImageSerializer
)
from apps.catalog.permissions import IsProductOwner, IsApprovedVendorPermission
from apps.core.pagination import StandardResultsSetPagination


def invalidate_product_cache():
    cache.delete_pattern('products_list_*')


class CategoryListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        categories = Category.objects.filter(is_active=True)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class TagListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)


class ProductListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'category', 'vendor', 'is_featured']
    search_fields = ['name', 'description', 'short_description', 'sku']
    ordering_fields = ['price', 'created_at', 'name', 'stock_quantity']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Product.objects.select_related('vendor', 'category').prefetch_related('images', 'tags')
        
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = tags.split(',')
            queryset = queryset.filter(tags__slug__in=tag_list).distinct()
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        cache_key = f'products_list_{hash(str(request.query_params))}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=300)
        
        return response


class ProductDetailView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, slug):
        cache_key = f'product_detail_{slug}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        product = get_object_or_404(
            Product.objects.select_related('vendor', 'category').prefetch_related('images', 'tags'),
            slug=slug
        )
        serializer = ProductDetailSerializer(product, context={'request': request})
        cache.set(cache_key, serializer.data, timeout=300)
        
        return Response(serializer.data)


class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated, IsApprovedVendorPermission]
    
    def post(self, request):
        serializer = ProductCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save(vendor=request.user.vendor_profile)
        
        invalidate_product_cache()
        
        return Response(ProductDetailSerializer(product, context={'request': request}).data, status=status.HTTP_201_CREATED)


class ProductUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsProductOwner]
    
    def get_object(self, slug):
        return get_object_or_404(Product, slug=slug)
    
    def put(self, request, slug):
        product = self.get_object(slug)
        self.check_object_permissions(request, product)
        
        serializer = ProductUpdateSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        invalidate_product_cache()
        cache.delete(f'product_detail_{slug}')
        
        return Response(ProductDetailSerializer(product, context={'request': request}).data)
    
    def delete(self, request, slug):
        product = self.get_object(slug)
        self.check_object_permissions(request, product)
        product.delete()
        
        invalidate_product_cache()
        cache.delete(f'product_detail_{slug}')
        
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_200_OK)


class ProductImageView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, slug):
        return get_object_or_404(Product, slug=slug)
    
    def post(self, request, slug):
        product = self.get_object(slug)
        
        if product.vendor.user != request.user:
            return Response({'error': 'You can only upload images for your own products'}, status=status.HTTP_403_FORBIDDEN)
        
        images = request.FILES.getlist('images')
        if not images:
            return Response({'error': 'No images provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_images = []
        for image in images:
            product_image = ProductImage.objects.create(
                product=product,
                image=image,
                alt_text=request.data.get('alt_text', ''),
                is_primary=request.data.get('is_primary', False),
                sort_order=request.data.get('sort_order', 0)
            )
            uploaded_images.append(ProductImageSerializer(product_image).data)
        
        invalidate_product_cache()
        cache.delete(f'product_detail_{slug}')
        
        return Response({'images': uploaded_images}, status=status.HTTP_201_CREATED)
    
    def get(self, request, slug):
        product = self.get_object(slug)
        images = ProductImage.objects.filter(product=product)
        serializer = ProductImageSerializer(images, many=True)
        return Response(serializer.data)    