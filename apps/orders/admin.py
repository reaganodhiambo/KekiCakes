"""KekiCakes – Orders Admin"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Customer, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('variant', 'cake_name', 'size_label', 'type_label', 'custom_message', 'quantity', 'unit_price', 'subtotal_display')
    fields = ('variant', 'cake_name', 'size_label', 'type_label', 'custom_message', 'quantity', 'unit_price', 'subtotal_display')

    @admin.display(description='Subtotal (KES)')
    def subtotal_display(self, obj):
        return f'KES {obj.get_subtotal():,.2f}'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'created_at')
    search_fields = ('name', 'phone', 'email')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_phone', 'status_badge', 'order_type', 'total_display', 'created_at')
    list_filter = ('status', 'order_type', 'created_at')
    search_fields = ('customer__name', 'customer__phone')
    readonly_fields = ('created_at', 'updated_at', 'total')
    inlines = [OrderItemInline]
    actions = ['mark_paid', 'mark_completed']

    @admin.display(description='Customer')
    def customer_name(self, obj):
        return obj.customer.name

    @admin.display(description='Phone')
    def customer_phone(self, obj):
        return obj.customer.phone

    @admin.display(description='Status')
    def status_badge(self, obj):
        colours = {
            'pending': '#f59e0b',
            'paid': '#3b82f6',
            'completed': '#10b981',
            'cancelled': '#ef4444',
        }
        colour = colours.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:9999px;font-size:12px">{}</span>',
            colour, obj.get_status_display()
        )

    @admin.display(description='Total (KES)')
    def total_display(self, obj):
        return f'KES {obj.total:,.2f}'

    @admin.action(description='Mark selected orders as Paid')
    def mark_paid(self, request, queryset):
        queryset.update(status='paid')

    @admin.action(description='Mark selected orders as Completed')
    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
