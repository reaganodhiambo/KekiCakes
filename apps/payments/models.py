"""
KekiCakes – Payment Model
Tracks M-Pesa STK Push transactions
"""
from django.db import models
from apps.orders.models import Order


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('timeout', 'Timeout'),
        ('cancelled', 'Cancelled'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    checkout_request_id = models.CharField(max_length=100, unique=True, db_index=True)
    merchant_request_id = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    mpesa_receipt = models.CharField(max_length=50, blank=True, help_text='M-Pesa confirmation code')
    transaction_date = models.CharField(max_length=20, blank=True)
    raw_callback = models.JSONField(null=True, blank=True, help_text='Raw M-Pesa IPN payload')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f'Payment for Order #{self.order.pk} – {self.status} ({"Receipt: " + self.mpesa_receipt if self.mpesa_receipt else "No receipt"})'
