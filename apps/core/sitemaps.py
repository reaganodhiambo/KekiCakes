from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.products.models import Cake, CakeCategory

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return ['core:home', 'products:shop', 'core:contact']

    def location(self, item):
        return reverse(item)

class CakeSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.7

    def items(self):
        return Cake.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return CakeCategory.objects.filter(is_active=True)
