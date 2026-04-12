"""KekiCakes – Core Models (Contact and Inquiry)"""
from django.db import models

class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.name} at {self.created_at.strftime('%Y-%m-%d')}"


class CakeInquiry(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    event_date = models.DateField(null=True, blank=True)
    cake_description = models.TextField(help_text="Detailed description of the custom order")
    budget = models.CharField(max_length=100, blank=True)
    is_addressed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Cake Inquiries'

    def __str__(self):
        return f"Inquiry from {self.name} for {self.event_date or 'TBD'}"
