from django.db import models
# Create your models here.
from django.db import models
from smart_selects.db_fields import ChainedForeignKey
from django.utils import timezone
from django.core.validators import RegexValidator
from django.db.models import IntegerField, Sum, F

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
        marks = Marks.objects.filter(marksheet__student=self)
        obtained = marks.aggregate(total=Sum(F('test_marks') + F('written_marks'), output_field=IntegerField()))['total'] or 0
        maximum = marks.aggregate(total=Sum(F('max_test_marks') + F('max_written_marks'), output_field=IntegerField()))['total'] or 0
        if maximum == 0:
            return 0
        return round((obtained / maximum) * 100, 2)

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
    academic_year = models.CharField(max_length=15, default="2025-2026")

    def __str__(self):
        return f"{self.name} ({self.academic_year})"
    

# =========================
# MARKSHEET MODEL
# =========================

class MarkSheet(models.Model):

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

    @property
    def calculate_grade(self):

        return grade(self.percentage)

    class Meta:

        unique_together = ['student', 'exam']

        verbose_name = "Marksheet"

        verbose_name_plural = "Marksheets"

    def __str__(self):

        return f"{self.student.name} - {self.exam.name}"


    # =========================
    # OBTAINED MARKS
    # =========================

    @property
    def obtained_marks(self):

        total = 0

        for mark in self.subject_marks.all():

            total += mark.obtained_total

        return total


    # =========================
    # GRAND TOTAL MARKS
    # =========================

    @property
    def grand_total_marks(self):
        total = 0
        for mark in self.subject_marks.all():
            total += mark.max_total
        return total


    # =========================
    # PERCENTAGE
    # =========================

    @property
    def percentage(self):

        if self.grand_total_marks == 0:
            return 0

        return round(
            (self.obtained_marks / self.grand_total_marks) * 100,
            2
        )


    # =========================
    # PASS / FAIL
    # =========================

    @property
    def result(self):

        if self.percentage >= 33:
            return "Pass"

        return "Fail"


    # =========================
    # GRADE
    # =========================

    @property
    def grade(self):

        percentage = self.percentage

        if percentage >= 90:
            return "A+"

        elif percentage >= 80:
            return "A"

        elif percentage >= 70:
            return "B"

        elif percentage >= 60:
            return "C"

        elif percentage >= 50:
            return "D"

        elif percentage >= 33:
            return "E"

        return "F"



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

        return (
            f"{self.subject.name} "
            f"({self.obtained_total}/{self.max_total})"
        )


    # =========================
    # OBTAINED TOTAL
    # =========================

   
    @property
    def obtained_total(self):
        return (
            (self.test_marks or 0) +
            (self.written_marks or 0)
        )


    # =========================
    # MAX TOTAL
    # =========================

    @property
    def max_total(self):
        return (
            (self.max_test_marks or 0) +
            (self.max_written_marks or 0)
        )


# Test MarkSheet



class TestMarkSheet(models.Model):
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam_name = models.ForeignKey(Exam, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.exam_name}"

    @property
    def total_obtained(self):
        return sum(i.obtained_marks for i in self.subject_marks.all())

    @property
    def total_max(self):
        return sum(i.max_marks for i in self.subject_marks.all())

    @property
    def percentage(self):
        if self.total_max == 0:
            return 0
        return round((self.total_obtained / self.total_max) * 100, 2)
    
    
class TestSubjectMark(models.Model):

    marksheet = models.ForeignKey(
        TestMarkSheet,
        on_delete=models.CASCADE,
        related_name='subject_marks'
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )


    obtained_marks = models.PositiveIntegerField(default=0)

    max_marks = models.PositiveIntegerField(default=15)

    remarks = models.CharField(
        max_length=100,
        blank=True
    )

    class Meta:
        unique_together = ('marksheet', 'subject')

    @property
    def grade(self):

        marks = self.obtained_marks

        if marks >= 14:
            return "A+"
        elif marks >= 12:
            return "A"
        elif marks >= 10:
            return "B"
        elif marks >= 8:
            return "C"
        elif marks >= 5:
            return "D"

        return "F"


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