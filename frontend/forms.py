# forms.py
from django import apps
from django import forms
from .models import AdmissionInquiry

class AdmissionInquiryForm(forms.ModelForm):
    class Meta:
        model = AdmissionInquiry
        fields = ['parent_name', 'contact_number', 'email_address', 'student_name', 'class_applying_for', 'message']
        
        # Adding widgets to match the styling/placeholders in your UI image
        widgets = {
            'parent_name': forms.TextInput(attrs={'placeholder': 'John Doe', 'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'placeholder': '+91 XXXXX XXXXX', 'class': 'form-control'}),
            'email_address': forms.EmailInput(attrs={'placeholder': 'parent@example.com', 'class': 'form-control'}),
            'student_name': forms.TextInput(attrs={'placeholder': "Child's Name", 'class': 'form-control'}),
            'class_applying_for': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'placeholder': 'Any specific requirements or queries...', 'rows': 4, 'class': 'form-control'}),
        }