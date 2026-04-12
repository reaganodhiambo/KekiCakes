from django.views.generic import TemplateView, View
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages
from apps.products.models import CakeCategory, Cake
from .forms import ContactForm, InquiryForm
import json


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = CakeCategory.objects.filter(is_active=True)
        ctx['featured_products'] = Cake.objects.filter(
            is_featured=True, is_active=True
        ).select_related('category')[:8]
        ctx['placeholder_categories'] = [
            {'name': 'Birthday', 'icon': ''},
            {'name': 'Wedding', 'icon': ''},
            {'name': 'Kids', 'icon': ''},
            {'name': 'Cupcakes', 'icon': ''},
            {'name': 'Custom', 'icon': ''},
        ]
        ctx['testimonials'] = [
            {
                'name': 'Amina Wanjiku',
                'text': 'The birthday cake was absolutely stunning! My daughter was over the moon. Will definitely order again.',
                'rating': 5,
                'avatar': '<img src="https://images.unsplash.com/photo-1531123897727-8f129e1eb44e?w=200&q=80" class="w-full h-full object-cover rounded-full">',
            },
            {
                'name': 'James Mutua',
                'text': 'Ordered a wedding cake and everyone kept asking who made it. Perfection in every slice!',
                'rating': 5,
                'avatar': '<img src="https://images.unsplash.com/photo-1506277886164-e25aa3f4ef7f?w=200&q=80" class="w-full h-full object-cover rounded-full">',
            },
            {
                'name': 'Grace Otieno',
                'text': 'Fast delivery, beautiful packaging and the red velvet was divine. 10/10!',
                'rating': 5,
                'avatar': '<img src="https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=200&q=80" class="w-full h-full object-cover rounded-full">',
            },
            {
                'name': 'Kevin Kamau',
                'text': 'The cupcakes for our office party were a huge hit. Fresh, moist and perfectly decorated.',
                'rating': 5,
                'avatar': '<img src="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&q=80" class="w-full h-full object-cover rounded-full">',
            },
        ]
        ctx['inquiry_form'] = InquiryForm()
        ctx['gallery_images'] = [
            {'url': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600&q=80', 'alt': 'Elegant chocolate cake'},
            {'url': 'https://images.unsplash.com/photo-1535254973040-607b474cb50d?w=600&q=80', 'alt': 'Tiered wedding cake'},
            {'url': 'https://images.unsplash.com/photo-1562440499-64c9a111f713?w=600&q=80', 'alt': 'Pink buttercream cake'},
            {'url': 'https://images.unsplash.com/photo-1464349095431-e9a21285b5f3?w=600&q=80', 'alt': 'Birthday celebration cake'},
            {'url': 'https://images.unsplash.com/photo-1558636508-e0db3814bd1d?w=600&q=80', 'alt': 'Cupcakes assortment'},
            {'url': 'https://images.unsplash.com/photo-1587668178277-295251f900ce?w=600&q=80', 'alt': 'Red velvet drip cake'},
            {'url': 'https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=600&q=80', 'alt': 'Pastel rainbow cake'},
            {'url': 'https://images.unsplash.com/photo-1621303837174-89787a7d4729?w=600&q=80', 'alt': 'Gold accent cake'},
        ]
        return ctx


class FeaturedCakesHTMXView(TemplateView):
    """HTMX lazy-load endpoint for featured cakes section."""

    def get(self, request, *args, **kwargs):
        products = Cake.objects.filter(
            is_featured=True, is_active=True
        ).select_related('category')[:8]
        html = render_to_string(
            'htmx/featured_cakes.html',
            {'products': products},
            request=request,
        )
        return HttpResponse(html)


class ContactView(TemplateView):
    template_name = 'core/contact.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = ContactForm()
        return ctx

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                send_mail(
                    subject=f"New Contact Message from {contact.name}",
                    message=f"Name: {contact.name}\nEmail: {contact.email}\nPhone: {contact.phone}\n\nMessage:\n{contact.message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['info@kekicakes.co.ke'],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, "Thank you! Your message has been sent. We'll get back to you shortly.")
            return redirect('core:contact')
        
        ctx = self.get_context_data()
        ctx['form'] = form
        return self.render_to_response(ctx)


class InquirySubmitView(View):
    def post(self, request, *args, **kwargs):
        form = InquiryForm(request.POST)
        if form.is_valid():
            inq = form.save()
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                send_mail(
                    subject=f"New Custom Cake Inquiry from {inq.name}",
                    message=f"Name: {inq.name}\nPhone: {inq.phone}\nEmail: {inq.email}\nTarget Date: {inq.delivery_date}\n\nDetails:\n{inq.details}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['info@kekicakes.co.ke'],
                    fail_silently=True,
                )
            except Exception:
                pass
                
            if request.headers.get('HX-Request'):
                html = "<div class='p-6 text-center'><h3 class='text-2xl text-rose font-display mb-2'>Inquiry Sent!</h3><p class='text-brown'>We'll be in touch soon.</p></div>"
                res = HttpResponse(html)
                res['HX-Trigger'] = json.dumps({'showToast': 'Inquiry successfully submitted!'})
                return res
            messages.success(request, "Inquiry received. We'll be in touch soon!")
            return redirect('core:home')
            
        if request.headers.get('HX-Request'):
            html = render_to_string('htmx/inquiry_form.html', {'inquiry_form': form}, request=request)
            return HttpResponse(html)
        return redirect('core:home')
