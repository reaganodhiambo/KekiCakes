"""
KekiCakes – Seed Script (Weight-Based Pricing)
Generates categories, flavours, cakes, and weight-price variants.
Run:  python manage.py shell < scripts/seed_new.py
"""
from decimal import Decimal
from apps.products.models import CakeCategory, CakeType, Cake, CakeVariant

def run():
    # Clean slate
    CakeVariant.objects.all().delete()
    Cake.objects.all().delete()
    CakeType.objects.all().delete()
    CakeCategory.objects.all().delete()

    # ── Categories ────────────────────────────────────────────
    print("Seeding Categories...")
    cat_birthday = CakeCategory.objects.create(name='Birthday', sort_order=1)
    cat_wedding  = CakeCategory.objects.create(name='Wedding', sort_order=2)
    cat_kids     = CakeCategory.objects.create(name='Kids', sort_order=3)
    cat_cupcakes = CakeCategory.objects.create(name='Cupcakes', sort_order=4)
    cat_custom   = CakeCategory.objects.create(name='Custom', sort_order=5)

    # ── Flavour Types ─────────────────────────────────────────
    print("Seeding Flavour Types...")
    vanilla    = CakeType.objects.create(name='Vanilla', description='Classic soft vanilla sponge with buttercream')
    chocolate  = CakeType.objects.create(name='Chocolate', description='Rich dark chocolate ganache layers')
    red_velvet = CakeType.objects.create(name='Red Velvet', description='Red velvet with cream cheese frosting')
    lemon      = CakeType.objects.create(name='Lemon', description='Zesty lemon drizzle with citrus glaze')
    strawberry = CakeType.objects.create(name='Strawberry', description='Fresh strawberry cream with berry compote')
    carrot     = CakeType.objects.create(name='Carrot', description='Spiced carrot cake with walnut cream cheese')

    all_types = [vanilla, chocolate, red_velvet, lemon, strawberry, carrot]

    # ── Weight tiers & price multipliers ─────────────────────
    # base_price is for 0.5kg; each step increases by ~60-80%
    weights = ['0.5kg', '1kg', '1.5kg', '2kg', '2.5kg', '3kg', '3.5kg', '4kg', '4.5kg', '5kg']
    multipliers = [1.0, 1.8, 2.5, 3.2, 3.9, 4.5, 5.0, 5.6, 6.1, 6.5]

    # ── Cake Definitions ──────────────────────────────────────
    print("Seeding Cakes & Variants...")
    cakes_data = [
        {
            'cat': cat_birthday,
            'name': 'Classic Vanilla Dream',
            'brief': 'Light & fluffy vanilla sponge with swirled buttercream',
            'desc': 'Our signature vanilla cake — light, moist, and beautifully decorated with hand-piped buttercream swirls. A timeless choice for birthday celebrations of all ages.',
            'base_price': 1200,
            'types': [vanilla, chocolate, strawberry],
            'featured': True,
        },
        {
            'cat': cat_birthday,
            'name': 'Red Velvet Surprise',
            'brief': 'Luxurious red velvet layers with cream cheese frosting',
            'desc': 'Deep crimson layers of moist red velvet cake paired with tangy cream cheese frosting. Decorated with white chocolate shavings and fresh berries.',
            'base_price': 1500,
            'types': [red_velvet],
            'featured': True,
        },
        {
            'cat': cat_wedding,
            'name': 'Elegant White Tier',
            'brief': 'Pristine white fondant with delicate sugar flowers',
            'desc': 'A stunning all-white wedding cake with hand-crafted sugar flowers and pearl detailing. Each tier is baked fresh with your choice of flavour. Perfect centrepiece for your special day.',
            'base_price': 2500,
            'types': [vanilla, chocolate, lemon],
            'featured': True,
        },
        {
            'cat': cat_wedding,
            'name': 'Gold Drip Romance',
            'brief': 'Ivory buttercream with 24k edible gold drip',
            'desc': 'Two-tone ivory and gold cake featuring a dramatic gold drip, adorned with fresh florals and macarons. Sophisticated flavour meets showstopping design.',
            'base_price': 2800,
            'types': [chocolate, red_velvet, strawberry],
            'featured': True,
        },
        {
            'cat': cat_kids,
            'name': 'Superhero Kids Cake',
            'brief': 'Vibrant fondant with your child\'s favourite character',
            'desc': 'Bright, bold, and packed with fun — this cake features hand-modelled fondant toppers of popular superhero characters. Soft sponge inside, pure excitement outside.',
            'base_price': 1400,
            'types': [vanilla, chocolate],
            'featured': True,
        },
        {
            'cat': cat_kids,
            'name': 'Rainbow Unicorn',
            'brief': 'Pastel layers with a magical unicorn horn topper',
            'desc': 'Six layers of rainbow-tinted vanilla sponge wrapped in pastel buttercream. Topped with a gold unicorn horn, ears, and edible flowers. Every little girl\'s dream.',
            'base_price': 1600,
            'types': [vanilla, strawberry],
            'featured': True,
        },
        {
            'cat': cat_custom,
            'name': 'Chocolate Truffle Bliss',
            'brief': 'Triple-chocolate indulgence with Belgian ganache',
            'desc': 'For the serious chocolate lover — three layers of dark, milk, and white chocolate cake drenched in Belgian ganache. Finished with hand-rolled truffles and cocoa dust.',
            'base_price': 1800,
            'types': [chocolate],
            'featured': True,
        },
        {
            'cat': cat_birthday,
            'name': 'Lemon Drizzle Delight',
            'brief': 'Tangy lemon sponge with citrus glaze and candied peel',
            'desc': 'A refreshing lemon cake with a zesty sugar glaze and decorative candied lemon peel. Light, tangy, and perfect for outdoor celebrations.',
            'base_price': 1300,
            'types': [lemon],
            'featured': False,
        },
        {
            'cat': cat_custom,
            'name': 'Carrot Walnut Harvest',
            'brief': 'Spiced carrot cake crowned with cream cheese swirls',
            'desc': 'Warmly spiced carrot cake with crushed walnuts, golden raisins, and a thick layer of cream cheese frosting. Rustic charm meets gourmet flavour.',
            'base_price': 1500,
            'types': [carrot],
            'featured': False,
        },
        {
            'cat': cat_cupcakes,
            'name': 'Assorted Cupcake Box',
            'brief': 'A curated box of our best-selling cupcake flavours',
            'desc': 'Handpicked selection of our most popular cupcakes — vanilla, chocolate, red velvet, and strawberry. Each beautifully piped and boxed for gifting or indulging.',
            'base_price': 800,
            'types': [vanilla, chocolate, red_velvet, strawberry],
            'featured': True,
        },
    ]

    for data in cakes_data:
        cake = Cake.objects.create(
            category=data['cat'],
            name=data['name'],
            brief=data['brief'],
            description=data['desc'],
            starting_price=Decimal(data['base_price']),
            is_featured=data['featured'],
        )

        for cake_type in data['types']:
            for weight, mult in zip(weights, multipliers):
                price = round(data['base_price'] * mult / 50) * 50  # round to nearest 50
                CakeVariant.objects.create(
                    cake=cake,
                    type=cake_type,
                    size=weight,
                    price=Decimal(price),
                )

    total_variants = CakeVariant.objects.count()
    total_cakes = Cake.objects.count()
    print(f"Seeding Complete! {total_cakes} cakes, {total_variants} variants created.")

run()
