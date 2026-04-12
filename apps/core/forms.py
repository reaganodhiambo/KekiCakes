from django import forms
from .models import ContactMessage, CakeInquiry

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'message']


class InquiryForm(forms.ModelForm):
    class Meta:
        model = CakeInquiry
        fields = ['name', 'email', 'phone', 'event_date', 'cake_description', 'budget']
