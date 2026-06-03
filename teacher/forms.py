from django import forms
from .models import Teacher


class TeacherForm(forms.ModelForm):

    class Meta:
        model = Teacher

        fields = [
            'first_name',
            'last_name',
            'photo',
            'date_of_birth',
            'gender',
            'blood_group',
            'email',
            'phone_number',
            'adhaar_number',
            'pan_number',
            'designation',
            'joining_date',
            'qualification',
            'experience_years',
            'is_active',
        ]

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control-file'}),
            'gender': forms.TextInput(attrs={'class': 'form-control'}),
            'adhaar_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'pan_number': forms.TextInput(attrs={'class': 'form-control'}),
            'designation': forms.Select(attrs={'class': 'select2'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.TextInput(attrs={'class': 'form-control'}),          
            'date_of_birth': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),

            'joining_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
        }