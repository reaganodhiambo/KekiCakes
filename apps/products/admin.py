"""KekiCakes – Products Admin"""
from django.contrib import admin
from django.utils.html import format_html
from .models import CakeCategory, Cake, CakeType, CakeVariant, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ('image', 'alt_text', 'sort_order')


class CakeVariantInline(admin.TabularInline):
    model = CakeVariant
    extra = 1
    fields = ('type', 'size', 'price', 'sku', 'is_available')


@admin.register(CakeCategory)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(CakeType)
class CakeTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Cake)
class CakeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'starting_price', 'is_featured', 'is_active', 'thumbnail_preview')
    list_editable = ('is_featured', 'is_active', 'starting_price')
    list_filter = ('category', 'is_featured', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [CakeVariantInline, ProductImageInline]
    fieldsets = (
        ('Basic Info', {
            'fields': ('category', 'name', 'slug', 'description', 'base_image')
        }),
        ('Display Pricing', {
            'fields': ('starting_price',)
        }),
        ('Options', {
            'fields': ('allows_custom_message', 'is_featured', 'is_active')
        }),
    )

    @admin.display(description='Thumbnail')
    def thumbnail_preview(self, obj):
        if obj.base_image:
            return format_html('<img src="{}" style="height:50px;border-radius:4px;" />', obj.base_image.url)
        return '—'
