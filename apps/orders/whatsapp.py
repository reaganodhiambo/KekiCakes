"""
KekiCakes – WhatsApp Integration
Constructs WhatsApp pre-filled order URLs.
"""
from urllib.parse import quote
from django.conf import settings


def cart_order_url(cart):
    """Generate WhatsApp click-to-chat URL for the entire cart."""
    number = settings.WHATSAPP_NUMBER
    
    if cart.is_empty():
        return f"https://wa.me/{number}"

    lines = ["*NEW ORDER FROM KEKICAKES*\n"]
    
    for item in cart:
        lines.append(f'Cake: *{item["cake_name"]}*')
        lines.append(f'Size: {item["size_label"]}')
        lines.append(f'Type: {item["type_label"]}')
        if item.get("custom_message"):
            lines.append(f'Message: "{item["custom_message"]}"')
        lines.append(f'Qty: {item["quantity"]}')
        lines.append(f'Price: KES {item["price_decimal"]:,.0f}')
        lines.append('---')

    lines.append(f'\n*Total Amount: KES {cart.get_total():,.0f}*')
    lines.append('\nHi, I would like to place this order please. Should I pay via M-Pesa?')
    
    text = '\n'.join(lines)
    return f"https://wa.me/{number}?text={quote(text)}"

def order_whatsapp_url(order):
    """Generate WhatsApp click-to-chat URL for an existing Order."""
    number = settings.WHATSAPP_NUMBER
    
    lines = [f"*ORDER #{order.pk} FALLBACK FROM KEKICAKES*\n"]
    
    for item in order.items.all():
        lines.append(f'Cake: *{item.cake_name}*')
        if item.size_label:
            lines.append(f'Size: {item.size_label}')
        if item.type_label:
            lines.append(f'Type: {item.type_label}')
        if item.custom_message:
            lines.append(f'Message: "{item.custom_message}"')
        lines.append(f'Qty: {item.quantity}')
        lines.append(f'Price: KES {item.unit_price:,.0f}')
        lines.append('---')

    lines.append(f'\n*Total Amount: KES {order.total:,.0f}*')
    lines.append('\nHi, my M-Pesa payment failed online. Can I please finish paying for this order manually?')
    
    text = '\n'.join(lines)
    return f"https://wa.me/{number}?text={quote(text)}"
