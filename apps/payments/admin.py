"""KekiCakes – Payments Admin"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'phone', 'amount_display', 'status_badge', 'mpesa_receipt', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('phone', 'mpesa_receipt', 'checkout_request_id')
    readonly_fields = ('checkout_request_id', 'merchant_request_id', 'raw_callback', 'created_at', 'updated_at')

    @admin.display(description='Amount (KES)')
    def amount_display(self, obj):
        return f'KES {obj.amount:,.2f}'

    @admin.display(description='Status')
    def status_badge(self, obj):
        colours = {
            'pending': '#f59e0b',
            'success': '#10b981',
            'failed': '#ef4444',
            'timeout': '#6b7280',
            'cancelled': '#6b7280',
        }
        colour = colours.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:9999px;font-size:12px">{}</span>',
            colour, obj.get_status_display()
        )
