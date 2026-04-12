"""KekiCakes – Core URLs"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('htmx/featured/', views.FeaturedCakesHTMXView.as_view(), name='htmx_featured'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('inquiry/submit/', views.InquirySubmitView.as_view(), name='inquiry_submit'),
]
