from django import forms
from django.apps import apps
from .models import TransferCertificate, Attendance, AcademicFee, FeeReceipt, StudentClass, AdmitCard


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
    # Overriding student_class correctly. 

    # Django will automatically map this to your model's student_class ForeignKey field.
    student_class = forms.ModelChoiceField(
        queryset=StudentClass.objects.all(), # Straightforward, standard implementation
        required=True,
        label="Student Class"
    )


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

        fee_type = cleaned_data.get('fee_type')
        installment = cleaned_data.get('installment')
        academic_fee = cleaned_data.get('academic_fee')
        van_fee = cleaned_data.get('van_fee')

        # 1. ACADEMIC FEE AMOUNT LOGIC
        if fee_type == 'ACADEMIC' and academic_fee and installment:
            if installment == 'FIRST':
                cleaned_data['amount'] = academic_fee.first_installment
            elif installment == 'SECOND':
                cleaned_data['amount'] = academic_fee.second_installment
            elif installment == 'THIRD':
                cleaned_data['amount'] = academic_fee.third_installment
            
            self.instance.amount = cleaned_data['amount']

        # 2. VAN FEE AMOUNT LOGIC
        elif fee_type == 'VAN' and van_fee and installment:
            if installment == 'FIRST':
                cleaned_data['amount'] = van_fee.first_installment
            elif installment == 'SECOND':
                cleaned_data['amount'] = van_fee.second_installment
            elif installment == 'THIRD':
                # Changed to add_error to make it target the field nicely in the UI
                self.add_error('installment', "Van Fee has only 2 installments. 'THIRD' is invalid.")

        return cleaned_data
    

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