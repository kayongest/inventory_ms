from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from inventory.models import InventoryItem, Category, InventoryChange
from users.models import CustomUser
from .serializers import (
    UserSerializer, 
    InventoryItemSerializer, 
    CategorySerializer, 
    InventoryChangeSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()  # Add this line
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'quantity']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'quantity', 'price', 'date_added']
    ordering = ['name']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return InventoryItem.objects.all()
        return InventoryItem.objects.filter(created_by=user)
    
    def perform_create(self, serializer):
        item = serializer.save(created_by=self.request.user)
        
        # Log the creation
        InventoryChange.objects.create(
            item=item,
            user=self.request.user,
            change_type='CREATE',
            previous_quantity=0,
            new_quantity=item.quantity,
            notes="Item created"
        )
    
    def perform_update(self, serializer):
        old_instance = self.get_object()
        old_quantity = old_instance.quantity
        item = serializer.save()
        new_quantity = item.quantity
        
        if old_quantity != new_quantity:
            # Log quantity change
            change_type = 'ADJUST'
            if new_quantity > old_quantity:
                change_type = 'ADD'
            elif new_quantity < old_quantity:
                change_type = 'REMOVE'
                
            InventoryChange.objects.create(
                item=item,
                user=self.request.user,
                change_type=change_type,
                previous_quantity=old_quantity,
                new_quantity=new_quantity,
                notes="Item updated"
            )
        else:
            # Log other updates
            InventoryChange.objects.create(
                item=item,
                user=self.request.user,
                change_type='UPDATE',
                previous_quantity=old_quantity,
                new_quantity=new_quantity,
                notes="Item details updated"
            )
    
    def perform_destroy(self, instance):
        # Log deletion
        InventoryChange.objects.create(
            item=instance,
            user=self.request.user,
            change_type='DELETE',
            previous_quantity=instance.quantity,
            new_quantity=0,
            notes="Item deleted"
        )
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        threshold = int(request.query_params.get('threshold', 10))
        queryset = self.get_queryset().filter(quantity__lte=threshold)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        category = request.query_params.get('category', None)
        min_price = request.query_params.get('min_price', None)
        max_price = request.query_params.get('max_price', None)
        
        queryset = self.get_queryset()
        
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )
        
        if category:
            queryset = queryset.filter(category__name=category)
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class InventoryChangeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InventoryChange.objects.all()  # Add this line
    serializer_class = InventoryChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['item', 'change_type', 'user']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return InventoryChange.objects.all()
        return InventoryChange.objects.filter(item__created_by=user)