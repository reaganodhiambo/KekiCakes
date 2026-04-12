"""KekiCakes – Orders URLs"""
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.CartView.as_view(), name='cart'),
    path('add/', views.AddToCartView.as_view(), name='add'),
    path('remove/', views.RemoveFromCartView.as_view(), name='remove'),
    path('update/', views.UpdateCartView.as_view(), name='update'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
]
