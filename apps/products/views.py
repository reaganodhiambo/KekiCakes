"""
KekiCakes – Products Views
Shop listing (with filters + live search via HTMX) and Product Detail
"""
from django.views.generic import DetailView, TemplateView
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q, Min
from .models import CakeCategory, Cake, CakeVariant, COLOR_CHOICES
import json


class ShopView(TemplateView):
    template_name = 'products/shop.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = CakeCategory.objects.filter(is_active=True)
        ctx['products'] = self._filtered_products()
        ctx['current_category'] = self.request.GET.get('category', '')
        ctx['current_min'] = self.request.GET.get('min_price', '')
        ctx['current_max'] = self.request.GET.get('max_price', '')
        ctx['query'] = self.request.GET.get('q', '')
        return ctx

    def _filtered_products(self):
        qs = Cake.objects.filter(is_active=True).select_related('category')
        q = self.request.GET.get('q', '').strip()
        category = self.request.GET.get('category', '').strip()
        min_price = self.request.GET.get('min_price', '').strip()
        max_price = self.request.GET.get('max_price', '').strip()

        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        if category:
            qs = qs.filter(category__slug=category)
        if min_price:
            try:
                qs = qs.filter(starting_price__gte=float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                qs = qs.filter(starting_price__lte=float(max_price))
            except ValueError:
                pass
        return qs


class ProductGridHTMXView(TemplateView):
    """HTMX endpoint – returns only the product grid partial after filtering."""

    def get(self, request, *args, **kwargs):
        qs = Cake.objects.filter(is_active=True).select_related('category')
        q = request.GET.get('q', '').strip()
        category = request.GET.get('category', '').strip()
        min_price = request.GET.get('min_price', '').strip()
        max_price = request.GET.get('max_price', '').strip()

        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        if category:
            qs = qs.filter(category__slug=category)
        if min_price:
            try:
                qs = qs.filter(starting_price__gte=float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                qs = qs.filter(starting_price__lte=float(max_price))
            except ValueError:
                pass

        html = render_to_string(
            'htmx/product_grid.html',
            {'products': qs},
            request=request,
        )
        return HttpResponse(html)


class ProductDetailView(DetailView):
    model = Cake
    template_name = 'products/detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Cake.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'variants__type')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cake = self.object
        
        # Get unique types available for this cake
        variants = cake.variants.filter(is_available=True).select_related('type')
        types = []
        seen_types = set()
        
        for v in variants:
            t_id = v.type.id if v.type else None
            t_name = v.type.name if v.type else 'Standard'
            if t_id not in seen_types:
                types.append({'id': t_id or '', 'name': t_name})
                seen_types.add(t_id)

        # Build weight-price map for the default type
        default_type_id = types[0]['id'] if types else ''
        weight_prices = []
        for v in variants.filter(type_id=default_type_id).order_by('size'):
            weight_prices.append({
                'key': v.size,
                'label': v.get_size_display(),
                'price': int(v.price),
                'variant_id': v.id,
            })

        ctx['available_types'] = sorted(types, key=lambda x: x['name'])
        ctx['weight_prices'] = json.dumps(weight_prices)
        ctx['color_choices'] = COLOR_CHOICES
        ctx['related'] = Cake.objects.filter(
            category=cake.category, is_active=True
        ).exclude(pk=cake.pk)[:4]
        return ctx

        
def variant_price_api(request, cake_id):
    """API endpoint to get price for a specific variant combination."""
    type_id = request.GET.get('type_id') or None
    size = request.GET.get('size')
    
    try:
        variant = CakeVariant.objects.get(cake_id=cake_id, type_id=type_id, size=size, is_available=True)
        return JsonResponse({'success': True, 'price': float(variant.price), 'variant_id': variant.id})
    except CakeVariant.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Not available'})


def weight_prices_api(request, cake_id):
    """API: get all weight-price combinations for a given cake + type."""
    type_id = request.GET.get('type_id') or None
    variants = CakeVariant.objects.filter(
        cake_id=cake_id, type_id=type_id, is_available=True
    ).order_by('size')
    
    data = []
    for v in variants:
        data.append({
            'key': v.size,
            'label': v.get_size_display(),
            'price': float(v.price),
            'variant_id': v.id,
        })
    return JsonResponse({'weights': data})
