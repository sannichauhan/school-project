from django import forms
from .models import TransferCertificate, Attendance, AcademicFee, FeeReceipt


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


class AcademicFeeForm(forms.ModelForm):

    class Meta:
        model = AcademicFee
        fields = '__all__'

        widgets = {
            'student_type': forms.Select(attrs={'class': 'form-control'}),
            'class_group': forms.Select(attrs={'class': 'form-control'}),
            'annual_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            'first_installment': forms.NumberInput(attrs={'class': 'form-control'}),
            'second_installment': forms.NumberInput(attrs={'class': 'form-control'}),
            'third_installment': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class FeeReceiptForm(forms.ModelForm):

    class Meta:
        model = FeeReceipt
        fields = '__all__'
        widgets = {
            'payment_date': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            ),
            'amount': forms.NumberInput(attrs={'readonly': 'readonly'}),
            
        }

    def clean(self):
        cleaned_data = super().clean()

        academic_fee = cleaned_data.get('academic_fee')
        installment = cleaned_data.get('installment')

        if academic_fee and installment:

            if installment == 'FIRST':
                cleaned_data['amount'] = academic_fee.first_installment

            elif installment == 'SECOND':
                cleaned_data['amount'] = academic_fee.second_installment

            elif installment == 'THIRD':
                cleaned_data['amount'] = academic_fee.third_installment

            self.instance.amount = cleaned_data['amount']

        return cleaned_data
    
