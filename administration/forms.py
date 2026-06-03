from django import forms
from .models import TransferCertificate, Attendance


class TransferCertificateForm(forms.ModelForm):
    class Meta:
        model = TransferCertificate
        fields = "__all__"

        widgets = {
            'application_date': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            ),
            'issue_date': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            ),
            'reason_for_leaving': forms.Textarea(
                attrs={'rows': 3}
            ),
            'remarks': forms.Textarea(
                attrs={'rows': 3}
            ),
        }

        

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
