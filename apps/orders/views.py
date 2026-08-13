"""Views for order management."""

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders import services
from apps.orders.models import Address, Order
from apps.orders.serializers import (
    AddressSerializer, OrderCreateSerializer, OrderDetailSerializer,
    OrderListSerializer, OrderStatusHistorySerializer
)


class AddressListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        addresses = Address.objects.filter(user=request.user)
        return Response(AddressSerializer(addresses, many=True).data)
    
    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            order = services.create_order(
                buyer=request.user,
                vendor_id=data['vendor'],
                shipping_address_id=data['shipping_address'],
                billing_address_id=data['billing_address'],
                items=data['items'],
                notes=data.get('notes', ''),
            )
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'error': 'Invalid vendor, address or product'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderDetailSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        queryset = Order.objects.select_related('buyer', 'vendor')
        if not (user.role == 'admin' or user.is_staff):
            if hasattr(user, 'vendor_profile'):
                queryset = queryset.filter(vendor=user.vendor_profile)
            else:
                queryset = queryset.filter(buyer=user)
        
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return Response(OrderListSerializer(queryset, many=True).data)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, order_number):
        order = get_object_or_404(
            Order.objects.select_related('buyer', 'vendor').prefetch_related('items', 'status_history'),
            order_number=order_number
        )
        if not (user_can_access(request.user, order)):
            return Response({'error': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)
        return Response(OrderDetailSerializer(order).data)


class OrderApprovalView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, order_number):
        if not (request.user.role == 'admin' or request.user.is_staff):
            return Response({'error': 'Admin only'}, status=status.HTTP_403_FORBIDDEN)
        order = get_object_or_404(Order, order_number=order_number)
        action = request.data.get('action')
        remarks = request.data.get('remarks', '')
        try:
            if action == 'approve':
                services.approve_order(order, request.user, remarks)
            elif action == 'reject':
                services.change_order_status(order, Order.Status.REJECTED, request.user, remarks)
            else:
                return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderDetailSerializer(order).data)


class OrderStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number)
        to_status = request.data.get('status')
        remarks = request.data.get('remarks', '')
        try:
            services.update_status_with_role(order, to_status, request.user, remarks)
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderDetailSerializer(order).data)


class OrderHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number)
        return Response(OrderStatusHistorySerializer(order.status_history.all(), many=True).data)


def user_can_access(user, order):
    return user.role == 'admin' or user.is_staff or order.buyer == user or order.vendor.user == user