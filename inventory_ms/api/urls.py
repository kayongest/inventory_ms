from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'items', views.InventoryItemViewSet)
router.register(r'changes', views.InventoryChangeViewSet)

# Add an API root view
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'categories': reverse('category-list', request=request, format=format),
        'items': reverse('item-list', request=request, format=format),
        'changes': reverse('inventorychange-list', request=request, format=format),
    })

urlpatterns = [
    path('', include(router.urls)),
    path('', api_root, name='api-root'),
    path('api-auth/', include('rest_framework.urls')),
] 