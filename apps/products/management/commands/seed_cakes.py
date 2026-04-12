from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import CakeCategory, CakeType, Cake, CakeVariant

class Command(BaseCommand):
    help = 'Seeds the database with initial cakes, categories, types, and variants.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Seeding database with cakes...'))

        # 1. Create Categories
        categories_data = [
            {'name': 'Birthday Cakes', 'description': 'Delicious cakes carefully crafted to celebrate your special birthday.', 'sort_order': 1},
            {'name': 'Wedding Cakes', 'description': 'Elegant and multi-tiered premium cakes for your unforgettable day.', 'sort_order': 2},
            {'name': 'Corporate Cakes', 'description': 'Professional custom-branded cakes for corporate events.', 'sort_order': 3},
            {'name': 'Anniversary Cakes', 'description': 'Romantic and specialized cakes for anniversaries.', 'sort_order': 4},
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = CakeCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description'], 'sort_order': cat_data['sort_order']}
            )
            categories[cat_data['name']] = cat
            action = 'Created' if created else 'Found'
            self.stdout.write(f"{action} category: {cat.name}")

        # 2. Create Types (Flavors)
        types_data = [
            {'name': 'Vanilla', 'description': 'Classic rich vanilla bean flavor.'},
            {'name': 'Chocolate', 'description': 'Deep and rich double-chocolate layers.'},
            {'name': 'Black Forest', 'description': 'Chocolate sponge, sweet cherries, and whipped cream.'},
            {'name': 'Red Velvet', 'description': 'Smooth cocoa-based red velvet with cream cheese frosting.'},
            {'name': 'Fruit Cake', 'description': 'Traditional rich fruit cake matured with premium brandies.'},
        ]

        cake_types = {}
        for type_data in types_data:
            t, created = CakeType.objects.get_or_create(
                name=type_data['name'],
                defaults={'description': type_data['description']}
            )
            cake_types[type_data['name']] = t
            action = 'Created' if created else 'Found'
            self.stdout.write(f"{action} type: {t.name}")

        # 3. Create Cakes and Variants
        cakes_data = [
            {
                'name': 'Classic Vanilla Delight',
                'category': categories['Birthday Cakes'],
                'brief': 'The perfect vanilla cake for any simple birthday.',
                'description': 'Our classic vanilla delight is made with real Madagascar vanilla beans, frosted with our signature light vanilla buttercream.',
                'is_featured': True,
                'starting_price': 1500.00,
                'flavor': cake_types['Vanilla'],
                'variants': [
                    {'size': '1kg', 'price': 1500.00},
                    {'size': '2kg', 'price': 2800.00},
                    {'size': '3kg', 'price': 4100.00},
                ]
            },
            {
                'name': 'Rich Black Forest Bliss',
                'category': categories['Birthday Cakes'],
                'brief': 'Indulgent Black Forest with fresh cherries.',
                'description': 'A beautiful multi-layered chocolate sponge cake with authentic kirsch-soaked cherries and fresh dairy cream.',
                'is_featured': True,
                'starting_price': 1800.00,
                'flavor': cake_types['Black Forest'],
                'variants': [
                    {'size': '1kg', 'price': 1800.00},
                    {'size': '2kg', 'price': 3500.00},
                ]
            },
            {
                'name': 'Romance Red Velvet',
                'category': 'Anniversary Cakes',
                'brief': 'A timeless classic for lovebirds.',
                'description': 'Rich buttermilk red velvet base paired perfectly with our house-made cream cheese icing.',
                'is_featured': False,
                'starting_price': 2000.00,
                'flavor': cake_types['Red Velvet'],
                'variants': [
                    {'size': '1kg', 'price': 2000.00},
                    {'size': '2kg', 'price': 3800.00},
                    {'size': '3kg', 'price': 5500.00},
                ]
            },
        ]

        for c_data in cakes_data:
            # Handle string category resolving vs object
            cat_obj = c_data['category'] if isinstance(c_data['category'], CakeCategory) else categories[c_data['category']]
            
            cake, created = Cake.objects.get_or_create(
                name=c_data['name'],
                defaults={
                    'category': cat_obj,
                    'brief': c_data['brief'],
                    'description': c_data['description'],
                    'is_featured': c_data['is_featured'],
                    'starting_price': c_data['starting_price'],
                }
            )
            action = 'Created' if created else 'Found'
            self.stdout.write(self.style.SUCCESS(f"{action} Cake: {cake.name}"))

            # Variants
            flavor = c_data['flavor']
            for v_data in c_data['variants']:
                variant, v_created = CakeVariant.objects.get_or_create(
                    cake=cake,
                    type=flavor,
                    size=v_data['size'],
                    defaults={
                        'price': v_data['price'],
                        'is_available': True,
                    }
                )
                v_action = 'Created' if v_created else 'Found'
                self.stdout.write(f"  -> {v_action} variant: {variant}")

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database!'))
