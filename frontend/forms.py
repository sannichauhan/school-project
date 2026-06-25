# forms.py
from django import forms
from .models import AdmissionInquiry

class AdmissionInquiryForm(forms.ModelForm):
    class Meta:
        model = AdmissionInquiry
        fields = ['parent_name', 'contact_number', 'email_address', 'student_name', 'class_applying_for', 'message']