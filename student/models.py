from django.db import models
# Create your models here.
from django.db import models
from smart_selects.db_fields import ChainedForeignKey
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum, F
from django.db.models.functions import Coalesce



class AcademicSession(models.Model):
    name = models.CharField(max_length=20, help_text="e.g., 2026-2027", null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    
    class  Meta:
        unique_together = ("start_date", "end_date")

class StudentClass(models.Model):
    """Represents a grade level/class (e.g., Grade 1, Nursery A)"""
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    def __str__(self):
        return f"{self.name}".strip()

class Section(models.Model):
    name = models.CharField(max_length=10, unique=True, help_text="e.g. A, B, C")
    
    def __str__(self):
        return self.name

class Address(models.Model):
    """Reusable address model for permanent and local addresses"""
    address_line = models.TextField()
    district = models.CharField(max_length=100)
    pin_code = models.CharField(
        max_length=6,
        validators=[RegexValidator(regex=r'^\d{6}$', message="Enter valid 6 digit PIN code")]
    )
    state = models.CharField(max_length=100, default="Uttar Pradesh")
    nationality = models.CharField(max_length=100, default="Indian")

    def __str__(self):
        return f"{self.address_line}, {self.district}, {self.pin_code}, {self.state}"
    

class TransportRoute(models.Model):
    route_name = models.CharField(max_length=100)
    yearly_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.route_name
    
# मान लेते हैं कि ये मॉडल्स पहले से इम्पोर्टेड या डिफाइंड हैं:
# StudentClass, Section, AcademicSession, Address, TransportRoute, Marks, StudentAcademicHistory

class Student(models.Model):
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others')]
    RELIGION_CHOICES = [
        ('Hindu', 'Hindu'), ('Islam', 'Islam'), ('Christian', 'Christian'),
        ('Buddhist', 'Buddhist'), ('Others', 'Others'),
    ]
    CATEGORY_CHOICES = [
        ('GENERAL', 'General'), ('OBC', 'OBC'), ('SC', 'SC'), ('ST', 'ST'),
    ]
    SCHOOL_CHOICES = [
        ('NAV CHETANA PUBLIC SCHOOL', 'NCPS'),
        ('KAUSHALYA DEVI GIRLS NAV CHETANA PUBLIC J.H.S', 'KDGNCPS'),
    ]
    FEE_TYPE_CHOICES = [
        ('QUARTERLY', 'Quarterly'), ('HALF_YEARLY', 'Half Yearly'), ('YEARLY', 'Yearly'),
    ]
    TRANSPORT_INSTALLMENT_CHOICES = [
        ('1_INSTALLMENT', 'Single Installment'), ('2_INSTALLMENT', 'Two Installments'),
    ]

    # Identity & Basic Info
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    religion = models.CharField(max_length=20, choices=RELIGION_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, null=True, blank=True)
    
    adhaar_number = models.CharField(
        max_length=12, unique=True, blank=True, null=True,
        validators=[RegexValidator(regex=r'^\d{12}$', message="Aadhaar must be 12 digits")]
    )    

    # Academic Info
    admission_class = models.ForeignKey('StudentClass', on_delete=models.PROTECT, related_name='students')
    section = models.ForeignKey('Section', on_delete=models.SET_NULL, null=True, blank=True)
    roll_number = models.IntegerField(default=0)
    
    # Family Info
    father_name = models.CharField(max_length=100)
    father_occupation = models.CharField(max_length=100, blank=True)
    mother_name = models.CharField(max_length=100)
    mother_occupation = models.CharField(max_length=100, blank=True)
    pen_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="PEN Number")
    contact_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^[6-9]\d{9}$', message="Enter valid 10 digit mobile number")]
    )
    session = models.ForeignKey('AcademicSession', null=True, on_delete=models.CASCADE)
    choose_school = models.CharField(max_length=100, choices=SCHOOL_CHOICES, null=True, blank=True)
    last_institution = models.CharField(max_length=150, blank=True, null=True)
    permanent_address = models.OneToOneField('Address', on_delete=models.CASCADE, related_name='permanent_for_student')
    local_address = models.OneToOneField('Address', on_delete=models.CASCADE, related_name='local_for_student', blank=True, null=True)
    
    date_of_application = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)    
    student_photo = models.ImageField(upload_to='students/', blank=True, null=True)
    conveyance_facility = models.BooleanField(default=False)

    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES, default='QUARTERLY')
    transport_route = models.ForeignKey('TransportRoute', on_delete=models.SET_NULL, null=True, blank=True)
    transport_installment_type = models.CharField(max_length=20, choices=TRANSPORT_INSTALLMENT_CHOICES, null=True, blank=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        # अगर नया छात्र है या रोल नंबर नहीं है, तो ऑटो-जनरेट करें
        if not self.roll_number or self.roll_number == 0:
            last_student = Student.objects.filter(
                admission_class=self.admission_class,
                session=self.session
            ).order_by('-roll_number').first()
            
            if last_student and last_student.roll_number:
                self.roll_number = last_student.roll_number + 1
            else:
                self.roll_number = 1001

        # पैरेंट क्लास के save() को कॉल करें
        super().save(*args, **kwargs)
        
        # नया छात्र होने पर ही पहली हिस्ट्री रो (Row) बनाएं
        if is_new:
            # Circular Import से बचने के लिए मॉडल को यहीं इम्पोर्ट करना सबसे सेफ है
            from .models import StudentAcademicHistory
            StudentAcademicHistory.objects.get_or_create(
                student=self,
                session=self.session,
                student_class=self.admission_class,
                defaults={'roll_number': self.roll_number, 'is_active': True}
            )

    def __str__(self):
        return f"{self.name} ({self.roll_number})"

    # ==============================================================================
    # प्रॉपर्टीज (Properties) एवं ऑप्टिमाइजेशन लॉजिक
    # ==============================================================================
    @property
    def current_academic_record(self):
        # caching तकनीक का उपयोग ताकि एक ही रिक्वेस्ट में बार-बार क्वेरी न चले
        if not hasattr(self, '_cached_academic_record'):
            self._cached_academic_record = self.academic_history.filter(is_active=True).first()
        return self._cached_academic_record

    @property
    def current_class(self):
        record = self.current_academic_record
        return record.student_class if record else self.admission_class

    @property
    def current_session(self):
        record = self.current_academic_record
        return record.session if record else self.session

    @property
    def calculate_percentage(self):
        # N+1 क्वेरी से बचने के लिए select_related और filter लगाया गया है
        marks_list = Marks.objects.filter(marksheet__student=self).select_related('marksheet__exam')
        total_score = 0
        max_marks = 0

        for mark in marks_list:
            total_score += (mark.test_marks or 0) + (mark.written_marks or 0)
            exam_name = mark.marksheet.exam.name.lower() if mark.marksheet and mark.marksheet.exam else ""
            
            # स्पेलिंग मिस्टेक फिक्स: 'quaterly' और 'quarterly' दोनों को सुरक्षित रूप से हैंडल किया गया है
            if 'quaterly' in exam_name or 'quarterly' in exam_name:
                max_marks += (mark.max_test_marks or 0)
            else:
                max_marks += ((mark.max_test_marks or 0) + (mark.max_written_marks or 0))

        if max_marks == 0:
            return 0
            
        return round((total_score / max_marks) * 100, 2)   

    @property
    def calculate_grade(self):
        percentage = self.calculate_percentage
        if percentage >= 90: return 'A+'
        elif percentage >= 80: return 'A'
        elif percentage >= 70: return 'B'
        elif percentage >= 60: return 'C'
        elif percentage >= 50: return 'D'
        elif percentage >= 33: return 'E'
        else: return 'F'
        
    @property
    def pass_status(self):
        return 'Pass' if self.calculate_percentage >= 33 else 'Fail'
    




class Exam(models.Model):
    name = models.CharField(max_length=50)
    term = models.CharField(max_length=20, blank=True, null=True)     
    academic_session = models.ForeignKey(
        AcademicSession, 
        on_delete=models.CASCADE, 
        related_name="exams",
        verbose_name="Academic Year",
        null=True,  
        blank=True  
    )

    def __str__(self):
        return f"{self.name} ({self.academic_session.name})"   


# =========================
# MARKSHEET MODEL
# =========================

class MarkSheet(models.Model):

    academic_session = models.ForeignKey(
        AcademicSession,
        on_delete=models.PROTECT,
        null=True,  
        blank=True 
    )

    student_class = models.ForeignKey(
        StudentClass, 
        on_delete=models.PROTECT,
        null=True,
    )

    student=ChainedForeignKey(
        Student, 
        chained_field="student_class",
        chained_model_field="admission_class",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.CASCADE,
        related_name="marksheets"
    ) 

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE
    )

    class Meta:

        unique_together = ['academic_session', 'student', 'exam']

        verbose_name = "Marksheet"

        verbose_name_plural = "Marksheets"

    def __str__(self):

        return f"{self.student.name} - {self.exam.name}"
    

    # 1. Total Obtain Marks (Test Marks) nikalne ke liye method
    @property
    def total_obtained_marks(self):
        # Coalesce se agar value NULL hogi toh woh usko 0 maan lega
        result = self.subject_marks.aggregate(
            total=Sum(Coalesce(F('test_marks'), 0) + Coalesce(F('written_marks'), 0))
        )
        return result['total'] or 0

    # 2. Total Max Marks nikalne ke liye method
    @property
    def total_max_marks(self):
        exam_name = self.exam.name.lower()
        
        # Agar exam Quarterly hai toh sirf max_test_marks jodo
        if 'quaterly' in exam_name or 'quarterly' in exam_name:
            result = self.subject_marks.aggregate(
                total=Sum(Coalesce(F('max_test_marks'), 0))
            )
        else:
            # Baaki exams ke liye dono jodo
            result = self.subject_marks.aggregate(
                total=Sum(Coalesce(F('max_test_marks'), 0) + Coalesce(F('max_written_marks'), 0))
            )
        return result['total'] or 0

    # 3. Percentage Calculate karne ke liye method
    @property
    def calculate_percentage(self):
        max_m = self.total_max_marks
        if max_m > 0:
            percentage = (self.total_obtained_marks / max_m) * 100
            return round(percentage, 2)
        return 0.0

    # 4. Pass / Fail Status nikalne ke liye method
    @property
    def result_status(self):
        # function calling hata kar direct property use ki
        if self.calculate_percentage >= 33:  
            return "Pass"
        return "Fail"

    # 5. Grade nikalne ke liye method
    @property
    def calculate_grade(self):
        per = self.calculate_percentage
        if per >= 85: return "A+"
        elif per >= 70: return "A"
        elif per >= 60: return "B"
        elif per >= 50: return "C"
        elif per >= 33: return "D"
        else: return "E (Fail)"

        
class Subject(models.Model):
    # Link to the StudentClass model instead of using choices
    student_class = models.ForeignKey(
        'StudentClass', 
        on_delete=models.CASCADE, 
        related_name='subjects'
    )
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    max_test_marks = models.IntegerField(default=15)
    max_written_marks = models.IntegerField(default=35)

    class Meta:
        # Prevents duplicate subjects in the same class (e.g., two "Maths" in Class 1)
        unique_together = ['name', 'student_class']
        ordering = ['order']

    def __str__(self):
        return f"{self.name} ({self.student_class.name})"


    


    

# =========================
# SUBJECT WISE MARKS
# =========================
class Marks(models.Model):

    marksheet = models.ForeignKey(
        MarkSheet,
        on_delete=models.CASCADE,
        related_name='subject_marks'
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )


    # =========================
    # OBTAINED MARKS
    # =========================

    test_marks = models.PositiveIntegerField(
        default=0,
        blank=True,
        null=True
    )

    written_marks = models.PositiveIntegerField(
        default=0,
        blank=True,
        null=True
    )


    # =========================
    # MAXIMUM MARKS
    # =========================

    max_test_marks = models.PositiveIntegerField(
        default=0
    )

    max_written_marks = models.PositiveIntegerField(
        default=0
    )


    class Meta:

        unique_together = ['marksheet', 'subject']

        verbose_name_plural = "Marks"



    def __str__(self):
        return f"{self.subject.name} ({self.obtained_total}/{self.max_total})"


    # =========================
    # OBTAINED TOTAL
    # =========================

   
    @property
    def obtained_total(self):
        return (self.test_marks or 0) + (self.written_marks or 0)


    # =========================
    # MAX TOTAL
    # =========================

    @property
    def max_total(self):
        # marksheet ke zariye exam ka naam check karenge
        if self.marksheet and self.marksheet.exam:
            exam_name = self.marksheet.exam.name.lower()
            if 'quaterly' in exam_name or 'quarterly' in exam_name:
                return self.max_test_marks or 0  # Quarterly mein sirf test marks max honge
        
        # Baaki sabhi exams ke liye dono ka sum
        return (self.max_test_marks or 0) + (self.max_written_marks or 0)
    
class StudentAcademicHistory(models.Model):
    """Tracks which class and section a student belonged to in any given session"""
    student = models.ForeignKey(
        'Student', 
        on_delete=models.CASCADE, 
        related_name='academic_history'
    )
    session = models.ForeignKey(
        'AcademicSession', 
        on_delete=models.CASCADE, 
        related_name='student_enrollments'
    )
    student_class = models.ForeignKey(
        'StudentClass', 
        on_delete=models.CASCADE, 
        related_name='class_enrollments'
    )
    roll_number = models.IntegerField()
    is_active = models.BooleanField(
        default=True, 
        help_text="Designates if this is the student's current active session/class."
    )
    promoted_status = models.CharField(
        max_length=20,
        choices=[('PROMOTED', 'Promoted'), ('RETAINED', 'Retained'), ('PENDING', 'Pending')],
        default='PENDING'
    )

    class Meta:
        unique_together = ['student', 'session']
        verbose_name = "Student Academic History"
        verbose_name_plural = "Student Academic Histories"

    def __str__(self):
        return f"{self.student.name} - {self.student_class} ({self.session})"

    def save(self, *args, **kwargs):
        # 1. ऑटोमैटिक रोल नंबर जनरेशन (यदि पहले से मौजूद न हो या 0 हो)
        if not self.roll_number or self.roll_number == 0:
            last_record = StudentAcademicHistory.objects.filter(
                student_class=self.student_class,
                session=self.session
            ).order_by('-roll_number').first()
            
            if last_record and last_record.roll_number:
                self.roll_number = last_record.roll_number + 1
            else:
                self.roll_number = 1001
        
        # 2. डेटाबेस इंटीग्रिटी: एक छात्र का एक समय पर सिर्फ एक ही रिकॉर्ड 'Active' होना चाहिए
        if self.is_active:
            StudentAcademicHistory.objects.filter(
                student=self.student, 
                is_active=True
            ).exclude(pk=self.pk).update(is_active=False)
            
        super().save(*args, **kwargs)


class StudentPromotionLog(models.Model):
    """Logs the explicit transaction of moving students from one session/class to the next"""
    student = models.ForeignKey(
        'Student', 
        on_delete=models.CASCADE, 
        related_name='promotions'
    )
    from_session = models.ForeignKey(
        'AcademicSession', on_delete=models.CASCADE, related_name='promotions_from'
    )
    to_session = models.ForeignKey(
        'AcademicSession', on_delete=models.CASCADE, related_name='promotions_to'
    )
    from_class = models.ForeignKey(
        'StudentClass', on_delete=models.CASCADE, related_name='promoted_from'
    )
    to_class = models.ForeignKey(
        'StudentClass', on_delete=models.CASCADE, related_name='promoted_to'
    )
    promoted_by = models.CharField(max_length=100, blank=True, null=True) 
    promotion_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Promoted {self.student.name} to {self.to_class} ({self.to_session})"
        
    def clean(self):
        super().clean()
        # लॉजिकल वैलिडेशन: पुराना और नया सेशन सेम नहीं हो सकता
        if self.from_session == self.to_session:
            raise ValidationError("Source (From) and target (To) sessions cannot be the same.")

    def save(self, *args, **kwargs):
        # यह सुनिश्चित करता है कि जब बैकएंड या स्क्रिप्ट से ऑब्जेक्ट बने, तब भी clean() वैलिडेशन चले
        self.full_clean()
        super().save(*args, **kwargs)
        