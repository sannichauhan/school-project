from django import forms


from django.forms import modelformset_factory

# from .models import Section, Student, Address, StudentClass, MarkSheet, Subject, Exam, TestSubjectMark, AcademicSession, StudentAcademicHistory

from .models import Student, Address, StudentClass, MarkSheet, Subject, Exam, AcademicSession, Section

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_line', 'post_office', 'district', 'pin_code', 'state', 'nationality']
        widgets = {
            'address_line': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street, House No, Landmark, Village Name'}),
            'post_office':forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'pin_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '6-digit PIN'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class StudentAllInOneForm(forms.ModelForm):
    class Meta:
        model = Student
        # We exclude the address fields because we handle them as separate form instances
        exclude = ['permanent_address', 'local_address', 'created_at', 'roll_number', 'section']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'admission_class': forms.Select(attrs={'class': 'select2'}),
            'section': forms.Select(attrs={'class': 'select2'}),
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
            'transport_route': forms.Select(attrs={'class': 'select2'}),
            'fee_type': forms.Select(attrs={'class': 'form-control'}),
            'transport_installment_type': forms.Select(attrs={'class': 'form-control'}),
        }
        
class StudentClassForm(forms.ModelForm):
    class Meta:
        model = StudentClass
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. Class 10, Nursery, Grade 1'
            }),
        }
        
class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. A, B, C'
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
        # 'academic_year' ki jagah ab 'academic_session' aayega
        fields = ['name', 'term', 'academic_session']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Pro Tip: Dropdown me sirf active sessions dikhane ke liye (Optional)
        self.fields['academic_session'].queryset = AcademicSession.objects.filter(is_active=True)
        
        # Agar aap chahte hain ki iska label form me "Academic Year" dikhe
        self.fields['academic_session'].label = "Academic Year"


class AcademicSessionForm(forms.ModelForm):
    class Meta:
        model = AcademicSession
        fields = ['name', 'start_date', 'end_date', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., 2026-2027'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'  # इससे कैलेंडर पॉपअप खुलेगा
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # लॉजिकल वैलिडेशन: End Date हमेशा Start Date के बाद होनी चाहिए
        if start_date and end_date and end_date <= start_date:
            raise forms.ValidationError({
                'end_date': "End date must be later than the start date."
            })

        return cleaned_data

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if end_date <= start_date:
                raise forms.ValidationError(
                    "End date must be greater than start date."
                )

        return cleaned_data



class StudentPromotionForm(forms.Form):
    current_session = forms.ModelChoiceField(
        queryset=AcademicSession.objects.all(),
        widget=forms.Select(attrs={'class': 'select2', 'id': 'id_current_session'}),
        required=True,
        label="Current Session"
    )
    promotion_from_class = forms.ModelChoiceField(
        queryset=StudentClass.objects.all(),
        widget=forms.Select(attrs={'class': 'select2', 'id': 'id_from_class'}),
        required=True,
        label="Promote From Class"
    )
    promote_session = forms.ModelChoiceField(
        queryset=AcademicSession.objects.all(),
        widget=forms.Select(attrs={'class': 'select2', 'id': 'id_promote_session'}),
        required=True,
        label="Promote To Session"
    )
    promotion_to_class = forms.ModelChoiceField(
        queryset=StudentClass.objects.all(),
        widget=forms.Select(attrs={'class': 'select2', 'id': 'id_to_class'}),
        required=True,
        label="Promote To Class"
    )

    def __init__(self, *args, **kwargs):
        # डायनेमिक फिल्टरिंग के लिए पैरामीटर्स निकालना
        current_session_id = kwargs.pop('current_session_id', None)
        from_class_id = kwargs.pop('from_class_id', None)
        
        super().__init__(*args, **kwargs)
        
        # यदि दोनों IDs मौजूद हैं, तो डेटा फ़ेच करें
        if current_session_id and from_class_id:
            # select_related('student') लगाने से N+1 क्वेरी की समस्या हल होती है
            self.fields['students'].queryset = StudentAcademicHistory.objects.filter(
                session_id=current_session_id,
                student_class_id=from_class_id,
                is_active=True
            ).select_related('student')
            
            # UX Improvement: चेकबॉक्स के पास दिखने वाले नाम को कस्टमाइज़ करना
            # अब टेम्पलेट में पूरा इतिहास दिखने के बजाय सिर्फ "Student Name (Roll: 1001)" दिखेगा
            self.fields['students'].label_from_instance = lambda obj: f"{obj.student.name} (Roll: {obj.roll_number})"

    def clean(self):
        cleaned_data = super().clean()
        current_session = cleaned_data.get('current_session')
        promote_session = cleaned_data.get('promote_session')

        # वैलिडेशन: दोनों सेशन एक जैसे नहीं होने चाहिए
        if current_session and promote_session and current_session == promote_session:
            # फील्ड स्पेसिफिक एरर ऐड करना (ताकि यह सीधे 'promote_session' ड्रॉपडाउन के नीचे लाल रंग में दिखे)
            self.add_error('promote_session', "Promote session cannot be the same as the current session.")
            
        return cleaned_data