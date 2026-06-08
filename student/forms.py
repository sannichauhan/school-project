from django import forms
from .models import Student, Address, StudentClass, MarkSheet, StudentPromotion, Subject, Exam, TestSubjectMark, AcademicSession
from django.forms import modelformset_factory

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_line', 'district', 'pin_code', 'state', 'nationality']
        widgets = {
            'address_line': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Street, House No, Landmark'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'pin_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '6-digit PIN'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
        }

class StudentAllInOneForm(forms.ModelForm):
    class Meta:
        model = Student
        # We exclude the address fields because we handle them as separate form instances
        exclude = ['permanent_address', 'local_address', 'created_at', 'roll_number']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'admission_class': forms.Select(attrs={'class': 'select2'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'select2'}),
            'religion': forms.Select(attrs={'class': 'select2'}),
            'category': forms.Select(attrs={'class': 'select2'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_application': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),            
            'adhaar_number': forms.TextInput(attrs={'class': 'form-control'}),
            'student_photo': forms.FileInput(attrs={'class': 'form-control-file'}),
            'pen_number': forms.TextInput(attrs={'class': 'form-control'}),
            'choose_school': forms.Select(attrs={'class': 'select2'}),
            'last_institution': forms.TextInput(attrs={'class': 'form-control'}),
            'father_occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'session': forms.Select(attrs={'class': 'select2'}),
        }
        
class StudentClassForm(forms.ModelForm):
    class Meta:
        model = StudentClass
        fields = ['name', 'section']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. Class 10, Nursery, Grade 1'
            }),
            'section': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. A, B, Blue'
            }),
        }

class MarkSheetForm(forms.ModelForm):

    class Meta:
        model = MarkSheet

        fields = "__all__"

        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'exam': forms.Select(attrs={'class': 'form-control'}),
            'test_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'written_marks': forms.NumberInput(attrs={'class': 'form-control'}),
        }



class StudentPromotionForm(forms.ModelForm):
    class Meta:
        model = StudentPromotion
        fields = "__all__"


class StudentPromotionForm(forms.ModelForm):
    class Meta:
        model = StudentPromotion
        fields = [
            'current_session',
            'promote_session',
            'promotion_from_class',
            'promotion_to_class'
        ]

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = [
            'student_class',
            'name',
            'order',
            'max_test_marks',
            'max_written_marks'
        ]

        widgets = {
            'student_class': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_test_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_written_marks': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    # 👇 YAHI PE JAYEGA
    def clean(self):
        cleaned_data = super().clean()
        test = cleaned_data.get("max_test_marks")
        written = cleaned_data.get("max_written_marks")

        if test is not None and test < 0:
            self.add_error('max_test_marks', "Test marks cannot be negative")

        if written is not None and written < 0:
            self.add_error('max_written_marks', "Written marks cannot be negative")

        return cleaned_data


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['name', 'term', 'academic_year']


class AcademicSessionForm(forms.ModelForm):
    class Meta:
        model = AcademicSession
        fields = ['start_year', 'end_year']
        widgets = {
            'start_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Start Year'
            }),
            'end_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'End Year'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_year = cleaned_data.get("start_year")
        end_year = cleaned_data.get("end_year")

        if start_year and end_year:
            if end_year <= start_year:
                raise forms.ValidationError(
                    "End year must be greater than start year."
                )

        return cleaned_data


# Test Marksheet
class TestSubjectMarkForm(forms.ModelForm):

    class Meta:
        model = TestSubjectMark

        fields = [
            'subject',
            'obtained_marks',
            'max_marks',
            'remarks'
        ]

        widgets = {
            'subject': forms.HiddenInput(),
            'max_marks': forms.HiddenInput()
        }