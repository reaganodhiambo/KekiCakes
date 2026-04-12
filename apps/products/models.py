"""
KekiCakes – Product Models
Includes CakeCategory, Cake, CakeType, CakeVariant, and ProductImage
"""
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class CakeCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'cake categories'
        ordering = ['sort_order', 'name']
        indexes = [models.Index(fields=['slug'])]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:shop') + f'?category={self.slug}'


class Cake(models.Model):
    category = models.ForeignKey(CakeCategory, on_delete=models.SET_NULL, null=True, related_name='cakes')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    brief = models.CharField(max_length=120, blank=True, help_text='Short one-liner for product cards')
    description = models.TextField()
    base_image = models.ImageField(upload_to='cakes/', blank=True, null=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    allows_custom_message = models.BooleanField(default=True)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Display price (From KES)')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['category', 'is_active']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'slug': self.slug})

    @property
    def primary_image(self):
        first = self.images.first()
        return first.image if first else self.base_image


class CakeType(models.Model):
    """Specific cake flavor/type (e.g., Chocolate, Red Velvet, Vanilla)."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


COLOR_CHOICES = [
    ('white', 'White'),
    ('pink', 'Pink'),
    ('blue', 'Blue'),
    ('red', 'Red'),
    ('gold', 'Gold'),
    ('purple', 'Purple'),
    ('custom', 'Custom (specify in message)'),
]


class CakeVariant(models.Model):
    """The final combinatory product a user purchases."""
    WEIGHT_CHOICES = [
        ('0.5kg', '0.5 KG'),
        ('1kg', '1 KG'),
        ('1.5kg', '1.5 KG'),
        ('2kg', '2 KG'),
        ('2.5kg', '2.5 KG'),
        ('3kg', '3 KG'),
        ('3.5kg', '3.5 KG'),
        ('4kg', '4 KG'),
        ('4.5kg', '4.5 KG'),
        ('5kg', '5 KG'),
    ]

    cake = models.ForeignKey(Cake, on_delete=models.CASCADE, related_name='variants')
    type = models.ForeignKey(CakeType, on_delete=models.SET_NULL, null=True, related_name='variants')
    size = models.CharField(max_length=20, choices=WEIGHT_CHOICES, help_text='Weight of the cake')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Price in KES')
    sku = models.CharField(max_length=50, blank=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('cake', 'type', 'size')
        ordering = ['cake', 'size']

    def __str__(self):
        type_name = self.type.name if self.type else 'Standard'
        return f'{self.cake.name} - {self.get_size_display()} ({type_name})'

    def save(self, *args, **kwargs):
        if not self.sku:
            type_abbr = self.type.name[:3].upper() if self.type else 'STD'
            size_clean = self.size.upper().replace('.', '').replace('KG', 'KG')
            self.sku = f'{self.cake.pk}-{type_abbr}-{size_clean}'
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(Cake, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return f'{self.product.name} – Image {self.sort_order}'
