"""KekiCakes – Payments URLs"""
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('pay/<int:order_id>/', views.InitiatePaymentView.as_view(), name='initiate'),
    path('mpesa/callback/', views.MpesaCallbackView.as_view(), name='mpesa_callback'),
    path('status/<int:order_id>/', views.PaymentStatusView.as_view(), name='status'),
    path('success/<int:order_id>/', views.PaymentSuccessView.as_view(), name='success'),
    path('failed/<int:order_id>/', views.PaymentFailedView.as_view(), name='failed'),
]
