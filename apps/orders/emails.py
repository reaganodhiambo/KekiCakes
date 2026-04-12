from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

def send_order_notifications(order, status='success'):
    """
    Sends an email to the customer and the store admin upon order success or failure.
    """
    customer_email = order.customer.email
    admin_email = settings.DEFAULT_FROM_EMAIL
    
    if not admin_email:
        return

    ctx = {'order': order, 'items': order.items.all(), 'status': status}
    
    if status == 'success':
        subject = f'Order Confirmation – KekiCakes #{order.pk}'
        html_content = render_to_string('emails/order_success.html', ctx)
    else:
        subject = f'Payment Failed – KekiCakes Order #{order.pk}'
        html_content = render_to_string('emails/order_failed.html', ctx)

    text_content = strip_tags(html_content)

    # Send to Admin
    msg_admin = EmailMultiAlternatives(
        f"[ADMIN] {subject}",
        text_content,
        admin_email,
        [admin_email]
    )
    msg_admin.attach_alternative(html_content, "text/html")
    msg_admin.send(fail_silently=True)

    # Send to Customer
    if customer_email:
        msg_cust = EmailMultiAlternatives(
            subject,
            text_content,
            admin_email,
            [customer_email]
        )
        msg_cust.attach_alternative(html_content, "text/html")
        msg_cust.send(fail_silently=True)
