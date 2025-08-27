from rest_framework import serializers
from inventory.models import InventoryItem, Category, InventoryChange
from users.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class InventoryItemSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    
    class Meta:
        model = InventoryItem
        fields = '__all__'

class InventoryChangeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    item_name = serializers.ReadOnlyField(source='item.name')
    
    class Meta:
        model = InventoryChange
        fields = '__all__'