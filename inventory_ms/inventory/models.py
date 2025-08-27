from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_items')
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class InventoryChange(models.Model):
    CHANGE_TYPES = (
        ('ADD', 'Add Stock'),
        ('REMOVE', 'Remove Stock'),
        ('ADJUST', 'Adjustment'),
        ('CREATE', 'Item Created'),
        ('UPDATE', 'Item Updated'),
        ('DELETE', 'Item Deleted'),
    )
    
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='changes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    change_type = models.CharField(max_length=10, choices=CHANGE_TYPES)
    previous_quantity = models.IntegerField()
    new_quantity = models.IntegerField()
    change_amount = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        # Calculate change amount automatically
        self.change_amount = self.new_quantity - self.previous_quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.item.name} - {self.change_type} by {self.user.username}"
    
    class Meta:
        ordering = ['-timestamp']