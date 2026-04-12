"""
KekiCakes – Session Cart
Handles cart operations utilizing the new CakeVariant model.
"""
from decimal import Decimal
from django.conf import settings
from apps.products.models import CakeVariant


class Cart:
    def __init__(self, request):
        """Initialize the cart."""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def _generate_key(self, variant_id, custom_message):
        """Generate a unique key for the cart item."""
        # Using a tuple string representation or simply concatenating
        return f"{variant_id}_{custom_message.strip().lower()}"

    def add(self, variant, custom_message='', color='white', quantity=1, update_quantity=False):
        """Add a CakeVariant to the cart or update its quantity."""
        variant_id = str(variant.id)
        key = self._generate_key(variant_id, custom_message)

        if key not in self.cart:
            self.cart[key] = {
                'quantity': 0,
                'price': str(variant.price),
                'variant_id': variant_id,
                'custom_message': custom_message,
                'color': color,
                'cake_name': variant.cake.name,
                'size_label': variant.get_size_display(),
                'type_label': variant.type.name if variant.type else 'Standard',
                'thumbnail': variant.cake.primary_image.url if variant.cake.primary_image else ''
            }

        if update_quantity:
            self.cart[key]['quantity'] = quantity
        else:
            self.cart[key]['quantity'] += quantity

        self.save()

    def update_quantity(self, key, quantity):
        """Update the quantity of a specific cart item by key."""
        if key in self.cart:
            if quantity > 0:
                self.cart[key]['quantity'] = quantity
            else:
                self.remove(key)
            self.save()

    def remove(self, key):
        """Remove a product from the cart."""
        if key in self.cart:
            del self.cart[key]
            self.save()

    def save(self):
        """Mark the session as modified to make sure it gets saved."""
        self.session.modified = True

    def __iter__(self):
        """Iterate over the items in the cart and prepare for display."""
        for key, item in self.cart.items():
            item_copy = item.copy()
            item_copy['key'] = key
            
            # Decimal conversion for calculations
            price = Decimal(item_copy['price'])
            item_copy['price_decimal'] = price
            item_copy['subtotal'] = price * item_copy['quantity']
            
            yield item_copy

    def __len__(self):
        """Count all items in the cart."""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total(self):
        """Calculate the total cost of the cart."""
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """Remove cart from session."""
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def is_empty(self):
        """Return True if the cart is empty."""
        return len(self) == 0
