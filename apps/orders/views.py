"""
KekiCakes – Orders Views
Cart management (HTMX) + Checkout + Order Confirmation
"""
import json
from django.views import View
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.contrib import messages

from apps.products.models import CakeVariant
from .cart import Cart
from .models import Customer, Order, OrderItem
from .whatsapp import cart_order_url


# ── Cart Views ────────────────────────────────────────────────────────────────

class CartView(TemplateView):
    template_name = 'orders/cart.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        ctx['cart'] = cart
        ctx['cart_items'] = list(cart)
        ctx['cart_total'] = cart.get_total()
        ctx['whatsapp_url'] = cart_order_url(cart) if not cart.is_empty() else '#'
        return ctx


class AddToCartView(View):
    """HTMX endpoint: POST to add a product variant to the cart."""

    def post(self, request):
        cart = Cart(request)
        variant_id = request.POST.get('variant_id')
        variant = get_object_or_404(CakeVariant, pk=variant_id, is_available=True, cake__is_active=True)
        
        custom_message = request.POST.get('custom_message', '').strip()
        color = request.POST.get('color', 'white').strip()
        try:
            quantity = max(1, int(request.POST.get('quantity', 1)))
        except (ValueError, TypeError):
            quantity = 1

        cart.add(variant=variant, custom_message=custom_message, color=color, quantity=quantity)

        # If HTMX request, return the cart count badge partial
        if request.headers.get('HX-Request'):
            html = render_to_string('htmx/cart_badge.html', {'cart': cart}, request=request)
            response = HttpResponse(html)
            response['HX-Trigger'] = json.dumps({'showToast': f'{variant.cake.name} added to cart!'})
            return response

        messages.success(request, f'"{variant.cake.name}" added to your cart.')
        return redirect('orders:cart')


class RemoveFromCartView(View):
    """HTMX endpoint: POST to remove an item from the cart."""

    def post(self, request):
        cart = Cart(request)
        key = request.POST.get('key', '')
        cart.remove(key)

        if request.headers.get('HX-Request'):
            return self._render_cart_partial(request, cart)
        return redirect('orders:cart')

    def _render_cart_partial(self, request, cart):
        html = render_to_string(
            'htmx/cart_items.html',
            {'cart': cart, 'cart_items': list(cart), 'cart_total': cart.get_total()},
            request=request,
        )
        return HttpResponse(html)


class UpdateCartView(View):
    """HTMX endpoint: POST to update item quantity."""

    def post(self, request):
        cart = Cart(request)
        key = request.POST.get('key', '')
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1
        cart.update_quantity(key, quantity)

        if request.headers.get('HX-Request'):
            html = render_to_string(
                'htmx/cart_items.html',
                {'cart': cart, 'cart_items': list(cart), 'cart_total': cart.get_total()},
                request=request,
            )
            return HttpResponse(html)
        return redirect('orders:cart')


# ── Checkout Views ────────────────────────────────────────────────────────────

class CheckoutView(TemplateView):
    template_name = 'orders/checkout.html'

    def get(self, request, *args, **kwargs):
        cart = Cart(request)
        if cart.is_empty():
            messages.warning(request, 'Your cart is empty. Add some cakes first!')
            return redirect('products:shop')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        ctx['cart'] = cart
        ctx['cart_items'] = list(cart)
        ctx['cart_total'] = cart.get_total()
        ctx['whatsapp_url'] = cart_order_url(cart)
        return ctx

    def post(self, request, *args, **kwargs):
        cart = Cart(request)
        if cart.is_empty():
            return redirect('products:shop')

        # Collect customer info
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()
        order_type = request.POST.get('order_type', 'delivery')
        notes = request.POST.get('notes', '').strip()

        if not name or not phone:
            messages.error(request, 'Name and phone number are required.')
            return self.get(request, *args, **kwargs)

        # Create customer & order
        customer, _ = Customer.objects.get_or_create(
            phone=phone,
            defaults={'name': name, 'email': email, 'address': address}
        )
        customer.name = name
        customer.email = email
        customer.address = address
        customer.save()

        order = Order.objects.create(
            customer=customer,
            order_type=order_type,
            delivery_address=address if order_type == 'delivery' else '',
            notes=notes,
            total=cart.get_total(),
        )

        # Create order items
        for item in cart:
            try:
                variant = CakeVariant.objects.get(pk=item['variant_id'])
            except CakeVariant.DoesNotExist:
                variant = None
                
            OrderItem.objects.create(
                order=order,
                variant=variant,
                cake_name=item.get('cake_name', 'Unknown Cake'),
                size_label=item.get('size_label', ''),
                type_label=item.get('type_label', ''),
                custom_message=item.get('custom_message', ''),
                quantity=item['quantity'],
                unit_price=item['price_decimal'],
            )

        # Store order id in session for payment page
        request.session['pending_order_id'] = order.pk
        cart.clear()
        return redirect('payments:initiate', order_id=order.pk)
