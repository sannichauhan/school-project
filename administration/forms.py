from django import forms
from django.apps import apps
from .models import TransferCertificate, Attendance, AdmitCard


class TransferCertificateForm(forms.ModelForm):
    class Meta:
        model = TransferCertificate
        fields = "__all__"

        widgets = {
            'application_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            'issue_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            'reason_for_leaving': forms.Textarea(
                attrs={'rows': 3, 'class': 'form-control'}
            ),
            'remarks': forms.Textarea(
                attrs={'rows': 3, 'class': 'form-control'}
            ),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

        

class AttendanceForm(forms.ModelForm):

    class Meta:
        model = Attendance
        fields = [
            'student',
            'student_class',
            'attendance_date',
            'status',
            'remarks'
        ]

        widgets = {
            'attendance_date': forms.DateInput(
                attrs={'type': 'date'}
            )
        }
    

class AdmitCardForm(forms.ModelForm):
    class Meta:
        model = AdmitCard
        fields = ['student', 'session', 'exam_type', 'exam_start_date', 'exam_end_date', 'remarks']
        
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'session': forms.Select(attrs={'class': 'form-control'}),
            'exam_type': forms.Select(attrs={'class': 'form-control'}),
            'exam_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'exam_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional remarks...'}),
        }
