from django.contrib import admin
from .models import ContactMessage, CakeInquiry

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'phone')
    actions = ['mark_read']

    @admin.action(description='Mark selected as read')
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)

@admin.register(CakeInquiry)
class CakeInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'event_date', 'created_at', 'is_addressed')
    list_filter = ('is_addressed', 'event_date', 'created_at')
    search_fields = ('name', 'phone')
    actions = ['mark_addressed']

    @admin.action(description='Mark selected as addressed')
    def mark_addressed(self, request, queryset):
        queryset.update(is_addressed=True)
