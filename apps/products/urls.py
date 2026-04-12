"""KekiCakes – Products URLs"""
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ShopView.as_view(), name='shop'),
    path('htmx/grid/', views.ProductGridHTMXView.as_view(), name='htmx_grid'),
    path('api/variant/<int:cake_id>/', views.variant_price_api, name='api_variant_price'),
    path('api/weights/<int:cake_id>/', views.weight_prices_api, name='api_weight_prices'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='detail'),
]
