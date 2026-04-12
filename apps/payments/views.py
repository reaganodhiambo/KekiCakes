"""
KekiCakes – Payment Views
STK Push initiation, IPN callback, status polling
"""
import json
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string

from apps.orders.models import Order
from apps.orders.cart import Cart
from .models import Payment
from .mpesa_service import MpesaService


class InitiatePaymentView(TemplateView):
    """Show payment page with order summary and trigger STK Push."""
    template_name = 'payments/initiate.html'

    def get(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, pk=order_id)
        # Verify it's the right user's order (session check)
        if request.session.get('pending_order_id') != order.pk:
            return redirect('core:home')
        return render(request, self.template_name, {
            'order': order,
            'items': order.items.select_related('product').all(),
        })

    def post(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, pk=order_id)
        phone = request.POST.get('phone', order.customer.phone)

        mpesa = MpesaService()
        result = mpesa.initiate_stk_push(
            phone_number=phone,
            amount=float(order.total),
            reference=f'ORD{order.pk}',
            description=f'Keki Cakes #{order.pk}',
        )

        if result.get('ResponseCode') == '0':
            # STK Push sent successfully
            Payment.objects.update_or_create(
                order=order,
                defaults={
                    'checkout_request_id': result.get('CheckoutRequestID', ''),
                    'merchant_request_id': result.get('MerchantRequestID', ''),
                    'phone': phone,
                    'amount': order.total,
                    'status': 'pending',
                },
            )
            if request.headers.get('HX-Request'):
                html = render_to_string(
                    'htmx/payment_polling.html',
                    {
                        'order': order,
                        'checkout_request_id': result.get('CheckoutRequestID'),
                    },
                    request=request,
                )
                return HttpResponse(html)
            return redirect('payments:status', order_id=order.pk)

        # STK Push failed
        error_msg = result.get('error', 'Payment initiation failed. Please try again.')
        if request.headers.get('HX-Request'):
            html = render_to_string(
                'htmx/payment_error.html',
                {'error': error_msg},
                request=request,
            )
            return HttpResponse(html, status=400)
        return render(request, self.template_name, {
            'order': order,
            'items': order.items.select_related('product').all(),
            'error': error_msg,
        })


@method_decorator(csrf_exempt, name='dispatch')
class MpesaCallbackView(View):
    """
    IPN endpoint called by Safaricom after STK Push completes.
    Must be publicly accessible (no CSRF).
    """

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, Exception):
            return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Invalid JSON'})

        callback = data.get('Body', {}).get('stkCallback', {})
        checkout_request_id = callback.get('CheckoutRequestID', '')
        result_code = callback.get('ResultCode')

        try:
            payment = Payment.objects.get(checkout_request_id=checkout_request_id)
        except Payment.DoesNotExist:
            return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})

        payment.raw_callback = data

        if result_code == 0:
            # Success – extract metadata
            meta_items = callback.get('CallbackMetadata', {}).get('Item', [])
            meta = {item['Name']: item.get('Value') for item in meta_items}
            payment.status = 'success'
            payment.mpesa_receipt = str(meta.get('MpesaReceiptNumber', ''))
            payment.transaction_date = str(meta.get('TransactionDate', ''))
            payment.order.status = 'paid'
            payment.order.save(update_fields=['status'])
        else:
            payment.status = 'failed'

        payment.save()
        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})


class PaymentStatusView(TemplateView):
    """Polling endpoint – returns current payment status (HTMX pings this)."""

    def get(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, pk=order_id)
        try:
            payment = order.payment
        except Payment.DoesNotExist:
            payment = None

        status = payment.status if payment else 'pending'

        if request.headers.get('HX-Request'):
            html = render_to_string(
                'htmx/payment_status.html',
                {'payment': payment, 'order': order, 'status': status},
                request=request,
            )
            response = HttpResponse(html)
            # Stop polling once terminal state reached
            if status in ('success', 'failed', 'timeout', 'cancelled'):
                response['HX-Trigger'] = 'paymentComplete'
            else:
                response['HX-Retarget'] = '#payment-status'
            return response

        # Full page
        if status == 'success':
            return redirect('payments:success', order_id=order.pk)
        if status in ('failed', 'timeout', 'cancelled'):
            return redirect('payments:failed', order_id=order.pk)

        return render(request, 'payments/waiting.html', {'order': order, 'payment': payment})


class PaymentSuccessView(TemplateView):
    template_name = 'payments/success.html'

    def get(self, request, order_id,  *args, **kwargs):
        order = get_object_or_404(Order, pk=order_id)
        # Clear the cart on successful payment
        cart = Cart(request)
        cart.clear()
        if 'pending_order_id' in request.session:
            del request.session['pending_order_id']
        return render(request, self.template_name, {
            'order': order,
            'payment': getattr(order, 'payment', None),
        })


class PaymentFailedView(TemplateView):
    template_name = 'payments/failed.html'

    def get(self, request, order_id, *args, **kwargs):
        order = get_object_or_404(Order, pk=order_id)
        return render(request, self.template_name, {
            'order': order,
            'payment': getattr(order, 'payment', None),
        })
