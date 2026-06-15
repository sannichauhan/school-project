from django.db import models
# Create your models here.
from django.db import models
from smart_selects.db_fields import ChainedForeignKey
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum, F
from django.db.models.functions import Coalesce

class Section(models.Model):
    name = models.CharField(max_length=10, unique=True, help_text="e.g. A, B, C")
    
    def __str__(self):
        return self.name

class StudentClass(models.Model):
    """Represents a grade level/class (e.g., Grade 1, Nursery A)"""
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    def __str__(self):
        return f"{self.name}".strip()


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

class AcademicSession(models.Model):
    name = models.CharField(max_length=20, help_text="e.g., 2026-2027", null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    
    class  Meta:
        unique_together = ("start_date", "end_date")
    
class StudentPromotion(models.Model):

    current_session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name="current_promotions"
    )

    promote_session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name="next_promotions"
    )

    promotion_from_class = models.ForeignKey(
        StudentClass,
        on_delete=models.CASCADE,
        related_name="promotion_from"
    )

    promotion_to_class = models.ForeignKey(
        StudentClass,
        on_delete=models.CASCADE,
        related_name="promotion_to"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.promotion_from_class} "
            f"-> {self.promotion_to_class}"
        )
class TransportRoute(models.Model):
    route_name = models.CharField(max_length=100)
    yearly_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.route_name
    
class Student(models.Model):
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others')]
    RELIGION_CHOICES = [
        ('Hindu', 'Hindu'), ('Islam', 'Islam'), ('Christian', 'Christian'),
        ('Buddhist', 'Buddhist'), ('Others', 'Others'),
    ]
    CATEGORY_CHOICES = [
        ('GENERAL', 'General'),
        ('OBC', 'OBC'),
        ('SC', 'SC'),
        ('ST', 'ST'),
    ]

    SCHOOL_CHOICES = [
        ('NAV CHETANA PUBLIC SCHOOL', 'NCPS'),
        ('KAUSHALYA DEVI GIRLS NAV CHETANA PUBLIC J.H.S', 'KDGNCPS'),
    ]
    
    FEE_TYPE_CHOICES = [
        ('QUARTERLY', 'Quarterly'),
        ('HALF_YEARLY', 'Half Yearly'),
        ('YEARLY', 'Yearly'),
    ]
    TRANSPORT_INSTALLMENT_CHOICES = [
        ('1_INSTALLMENT', 'Single Installment'),
        ('2_INSTALLMENT', 'Two Installments'),
    ]

    # Identity & Basic Info
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    
    religion = models.CharField(max_length=20, choices=RELIGION_CHOICES)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        null=True,
        blank=True
    )
    adhaar_number = models.CharField(
        max_length=12, unique=True, blank=True, null=True,
        validators=[RegexValidator(regex=r'^\d{12}$', message="Aadhaar must be 12 digits")]
    )    

    # Academic Info
    admission_class = models.ForeignKey(
    StudentClass, 
        on_delete=models.PROTECT,  # This prevents deleting a Class if students are in it
        related_name='students'
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    roll_number = models.IntegerField(
        default=0
    )
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
    session=models.ForeignKey(
        AcademicSession,
        null=True,
        on_delete=models.CASCADE
    )
    choose_school = models.CharField(
        max_length=100,
        choices=SCHOOL_CHOICES,
        null=True,
        blank=True
    )
    last_institution = models.CharField(max_length=150, blank=True, null=True)
    permanent_address = models.OneToOneField(
        Address, 
        on_delete=models.CASCADE, 
        related_name='permanent_for_student'
    )
    local_address = models.OneToOneField(
        Address, 
        on_delete=models.CASCADE, 
        related_name='local_for_student', 
        blank=True, 
        null=True
    )
    date_of_application = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)    
    student_photo = models.ImageField(upload_to='students/', blank=True, null=True)
    conveyance_facility = models.BooleanField(default=False)

    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES, default='QUARTERLY')
    transport_route = models.ForeignKey(TransportRoute, on_delete=models.SET_NULL, null=True, blank=True)
    transport_installment_type = models.CharField(max_length=20, choices=TRANSPORT_INSTALLMENT_CHOICES, null=True, blank=True)

    
        
    def save(self, *args, **kwargs):
        if not self.roll_number or self.roll_number == 0:
            # वर्तमान सेशन और क्लास के आखरी छात्र को ढूंढें
            last_student = Student.objects.filter(
                admission_class=self.admission_class,
                session=self.session
            ).order_by('-roll_number').first()
            
            if last_student and last_student.roll_number:
                self.roll_number = last_student.roll_number + 1
            else:
                self.roll_number = 1001 # शुद्ध इंटीजर असाइनमेंट
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.roll_number})"
    


    @property
    def current_academic_record(self):
        """Returns the active session and class details for the student"""
        return self.academic_history.filter(is_active=True).first()

    @property
    def current_class(self):
        record = self.current_academic_record
        return record.student_class if record else self.admission_class

    @property
    def current_session(self):
        record = self.current_academic_record
        return record.session if record else self.session

    # Automatically create the initial History record upon registration
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            StudentAcademicHistory.objects.create(
                student=self,
                session=self.session,
                student_class=self.admission_class,
                roll_number=self.roll_number,
                is_active=True
            )

    @property
    def calculate_percentage(self):
        # 1. Fetch all marks with related data in one go (Same as view)
        marks_list = Marks.objects.filter(
            marksheet__student=self
        ).select_related('marksheet__exam')
        
        total_score = 0
        max_marks = 0

        for mark in marks_list:
            # Obtained marks summation
            total_score += (mark.test_marks or 0) + (mark.written_marks or 0)
            
            # Max marks calculation based on exam name logic (Same as view)
            exam_name = mark.marksheet.exam.name.lower() if mark.marksheet and mark.marksheet.exam else ""
            
            if 'quaterly' in exam_name:
                max_marks += (mark.max_test_marks or 0)
            else:
                max_marks += (
                    (mark.max_test_marks or 0) +
                    (mark.max_written_marks or 0)
                )

        # 2. Percentage calculation
        if max_marks == 0:
            return 0
            
        return round((total_score / max_marks) * 100, 2)   

    
    @property
    def calculate_grade(self):
        percentage = self.calculate_percentage  # Upar banayi hui property ko call kiya
        
        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B'
        elif percentage >= 60:
            return 'C'
        elif percentage >= 50:
            return 'D'
        elif percentage >= 33:
            return 'E'
        else:
            return 'F'
        
    @property
    def pass_status(self):
        percentage = self.calculate_percentage # Purani property se percentage li
        
        # Agar 33% se kam hai toh Fail, warna Pass
        if percentage >= 33:
            return 'Pass'
        else:
            return 'Fail'
    
    
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

class Exam(models.Model):
    """Examples: Unit Test 1, Half Yearly, Final Exam"""
    name = models.CharField(max_length=50)
    term = models.CharField(max_length=20, blank=True, null=True) # e.g., Term 1
    
    # CharField ko hata kar ForeignKey add kiye hain
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
        AcademicSession, 
        on_delete=models.CASCADE, 
        related_name='student_enrollments'
    )
    student_class = models.ForeignKey(
        StudentClass, 
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
        choices=[('PROMOTED', 'Promoted'), ('DETAINED', 'Detained'), ('PENDING', 'Pending')],
        default='PENDING'
    )

    class Meta:
        unique_together = ['student', 'session']
        verbose_name = "Student Academic History"
        verbose_name_plural = "Student Academic Histories"

    def __str__(self):
        return f"{self.student.name} - {self.student_class} ({self.session})"

    def save(self, *args, **kwargs):
        # Handle automatic roll number generation if not provided
        if not self.roll_number or self.roll_number == 0:
            last_record = StudentAcademicHistory.objects.filter(
                student_class=self.student_class,
                session=self.session
            ).order_by('-roll_number').first()
            
            if last_record and last_record.roll_number:
                self.roll_number = last_record.roll_number + 1
            else:
                self.roll_number = 1001
        
        # Ensure only one record is 'active' for a student at a time
        if self.is_active:
            StudentAcademicHistory.objects.filter(student=self.student, is_active=True).exclude(pk=self.pk).update(is_active=False)
            
        super().save(*args, **kwargs)


class StudentPromotionLog(models.Model):
    """Logs the explicit transaction of moving students from one session/class to the next"""
    student = models.ForeignKey(
        'Student', 
        on_delete=models.CASCADE, 
        related_name='promotions'
    )
    from_session = models.ForeignKey(
        AcademicSession, on_delete=models.CASCADE, related_name='promotions_from'
    )
    to_session = models.ForeignKey(
        AcademicSession, on_delete=models.CASCADE, related_name='promotions_to'
    )
    from_class = models.ForeignKey(
        StudentClass, on_delete=models.CASCADE, related_name='promoted_from'
    )
    to_class = models.ForeignKey(
        StudentClass, on_delete=models.CASCADE, related_name='promoted_to'
    )
    promoted_by = models.CharField(max_length=100, blank=True, null=True) # Optional: track user
    promotion_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Promoted {self.student.name} to {self.to_class} ({self.to_session})"
        
    def clean(self):
        if self.from_session == self.to_session:
            raise ValidationError("Source and target sessions cannot be the same.")
        