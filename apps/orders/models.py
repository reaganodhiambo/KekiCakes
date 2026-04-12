"""
KekiCakes – Orders Models
Includes Customer, Order, and OrderItem
"""
from django.db import models
from apps.products.models import CakeVariant

class Customer(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, unique=True, help_text="M-Pesa registered number")
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid & Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    TYPE_CHOICES = [
        ('delivery', 'Delivery'),
        ('pickup', 'Store Pickup'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    order_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='delivery')
    delivery_address = models.TextField(blank=True, help_text="Used if type is delivery")
    notes = models.TextField(blank=True, help_text="Special instructions")

    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f'Order #{self.pk} – {self.customer.name}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(CakeVariant, on_delete=models.SET_NULL, null=True)
    
    # Store historic data in case variant is deleted or changed
    cake_name = models.CharField(max_length=200)
    size_label = models.CharField(max_length=50)
    type_label = models.CharField(max_length=100)
    
    custom_message = models.CharField(max_length=100, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity}x {self.cake_name}'

    def get_subtotal(self):
        return self.unit_price * self.quantity
