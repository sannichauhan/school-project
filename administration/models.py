from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from student.models import Student, AcademicSession, Exam, StudentClass
from smart_selects.db_fields import ChainedForeignKey
import uuid
from django.db.models import Sum
# Create your models here.
    
class AdmitCard(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        null=True
    )

    exam_type = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        null=True
    )

    exam_start_date = models.DateField(
        null=True,
        blank=True
    )

    exam_end_date = models.DateField(
        null=True,
        blank=True
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        default=timezone.now
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:        
        ordering = ['-created_at']
        unique_together = ['student', 'session']
        verbose_name = "Admit Card"
        verbose_name_plural = "Admit Cards"    
        managed=True

    def __str__(self):

        return (
            f"{self.student.name} - "
            f"{self.exam_type}"
        )

class TransferCertificate(models.Model):

    student_class = models.ForeignKey(
        StudentClass,
        on_delete=models.CASCADE,
        null=True,
    )

    student = ChainedForeignKey(
        Student,
        chained_field="student_class",
        chained_model_field="admission_class",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.CASCADE,
        related_name="transfer_certificates",
        null=True,
        blank=True
    ) 

       

    apar_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    last_class_studied = models.ForeignKey(
        StudentClass,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transfer_last_classes'
    )


    sr_no = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )


   

    total_working_days = models.IntegerField(
        default=0
    )

    total_present_days = models.IntegerField(
        default=0
    )

    general_conduct = models.CharField(
        max_length=100,
        default='Good'
    )

    application_date = models.DateField(
        default=timezone.now
    )

    issue_date = models.DateField(
        default=timezone.now
    )

    reason_for_leaving = models.TextField(
        blank=True,
        null=True
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def udise_code(self):
        if not self.student:
            return ""

        school = self.student.choose_school

        school_codes = {
            'NAV CHETANA PUBLIC SCHOOL': '09591001109',
            'KAUSHALYA DEVI GIRLS NAV CHETANA PUBLIC J.H.S': '09591001108',
        }

        return school_codes.get(school, '')

    def __str__(self):

        if self.student:
            return f"TC - {self.student.name}"

        return "Transfer Certificate"  




class Attendance(models.Model):
    ATTENDANCE_STATUS = (
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Leave'),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )

    student_class = models.ForeignKey(
        StudentClass,
        on_delete=models.CASCADE
    )

    attendance_date = models.DateField()

    status = models.CharField(
        max_length=1,
        choices=ATTENDANCE_STATUS,
        default='P'
    )

    remarks = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'attendance_date')
        ordering = ['-attendance_date']

    def __str__(self):
        return f"{self.student.name} - {self.attendance_date} - {self.get_status_display()}"
    

class AcademicFee(models.Model):

    STUDENT_TYPE = (
        ('NEW', 'New Student'),
        ('OLD', 'Old Student'),
    )

    CLASS_GROUP = (
        ('NUR_UKG', 'Nursery to UKG'),
        ('I_V', 'Class I to V'),
        ('VI_VIII', 'Class VI to VIII'),
    )

    student_type = models.CharField(
        max_length=10,
        choices=STUDENT_TYPE
    )

    class_group = models.CharField(
        max_length=20,
        choices=CLASS_GROUP
    )

    annual_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    first_installment = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    second_installment = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    third_installment = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.get_student_type_display()} - {self.get_class_group_display()}"
    

    def clean(self):
        from django.core.exceptions import ValidationError
        # Validate that installments equal the total annual fee
        total_installments = self.first_installment + self.second_installment + self.third_installment
        if total_installments != self.annual_fee:
            raise ValidationError(f"Sum of installments (₹{total_installments}) must equal Annual Fees (₹{self.annual_fee})")



class VanFee(models.Model):
    ROUTE_CHOICES = [
        ('GROUP_1', 'Pandey Tola / Jhankaul / Tendua / Amwa / Belwa'),
        ('GROUP_2', 'Barwa Sukdev / Basdila'),
        ('GROUP_3', 'Belwa Buzurg / Tejwaliya / Dhanauji'),
    ]
    
    route_group = models.CharField(max_length=20, choices=ROUTE_CHOICES, unique=True)
    annual_fee = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    first_installment = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="1st Installment (At Admission)")
    second_installment = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Van Fee: {self.get_route_group_display()}"

    def clean(self):
        from django.core.exceptions import ValidationError
        total_installments = self.first_installment + self.second_installment
        if total_installments != self.annual_fee:
            raise ValidationError(f"Sum of installments (₹{total_installments}) must equal Annual Fees (₹{self.annual_fee})")
    



class FeeReceipt(models.Model):
    INSTALLMENT_CHOICES = (('FIRST', '1st Installment'), ('SECOND', '2nd Installment'), ('THIRD', '3rd Installment'))
    FEE_TYPE = (('ACADEMIC', 'Academic Fee'), ('VAN', 'Van Fee'))

    fee_type = models.CharField(max_length=20, choices=FEE_TYPE, default='ACADEMIC')
    receipt_no = models.CharField(max_length=50, unique=True, editable=False)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE, null=True)
    
    student = ChainedForeignKey(
        Student, chained_field="student_class", chained_model_field="admission_class",
        show_all=False, auto_choose=True, sort=True, on_delete=models.CASCADE,
        related_name="fee_receipts", null=True, blank=True
    )

    academic_fee = models.ForeignKey(AcademicFee, on_delete=models.PROTECT, null=True, blank=True)
    van_fee = models.ForeignKey(VanFee, on_delete=models.PROTECT, null=True, blank=True)
    
    installment = models.CharField(max_length=10, choices=INSTALLMENT_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="System calculated expected amount")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Actual Amount Paid")
    
    payment_date = models.DateField(default=timezone.now)
    payment_mode = models.CharField(max_length=20, default='Cash')
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'fee_type', 'installment']

    def __str__(self):
        return self.receipt_no
    
    def clean(self):
        if self.fee_type == 'VAN':
            if not self.van_fee:
                raise ValidationError("Please select Van Fee for VAN type receipt.")
            if self.installment == 'THIRD':
                raise ValidationError("Van Fee has only 2 installments.")
        
        if self.fee_type == 'ACADEMIC' and not self.academic_fee:
            raise ValidationError("Please select Academic Fee for ACADEMIC type receipt.")

    def save(self, *args, **kwargs):
        # 1. Auto Receipt Number Generation
        if not self.receipt_no:
            today = timezone.now()
            last_receipt = FeeReceipt.objects.filter(created_at__year=today.year).order_by('-id').first()
            last_no = 0
            if last_receipt:
                try:
                    last_no = int(last_receipt.receipt_no.split('-')[-1])
                except ValueError:
                    last_no = 0
            self.receipt_no = f"RCPT-{today.year}-{last_no + 1:04d}"

        # 2. Setting auto amount by installment
        if self.fee_type == 'ACADEMIC' and self.academic_fee:
            if self.installment == 'FIRST':
                self.amount = self.academic_fee.first_installment
            elif self.installment == 'SECOND':
                self.amount = self.academic_fee.second_installment
            elif self.installment == 'THIRD':
                self.amount = self.academic_fee.third_installment
        elif self.fee_type == 'VAN' and self.van_fee:
            if self.installment == 'FIRST':
                self.amount = self.van_fee.first_installment
            elif self.installment == 'SECOND':
                self.amount = self.van_fee.second_installment

        # Call the parent's save method.
        super().save(*args, **kwargs)

        # 3. Syncing and calculating StudentFeeDue (Fix Bug)
        fee_due, created = StudentFeeDue.objects.get_or_create(
            student=self.student,
            defaults={
                'academic_fee': self.academic_fee,
                'van_fee': self.van_fee if self.fee_type == 'VAN' else None
            }
        )
        
        # If van fees are added later, please update them.
        if self.fee_type == 'VAN' and not fee_due.van_fee:
            fee_due.van_fee = self.van_fee

        # Filter and calculate Academic and Van deposit amount separately
        total_academic_paid = FeeReceipt.objects.filter(
            student=self.student, fee_type='ACADEMIC'
        ).aggregate(total=Sum('paid_amount'))['total'] or 0

        total_van_paid = FeeReceipt.objects.filter(
            student=self.student, fee_type='VAN'
        ).aggregate(total=Sum('paid_amount'))['total'] or 0

        fee_due.paid_amount = total_academic_paid
        fee_due.van_paid_amount = total_van_paid
        fee_due.save() # This method will trigger the following save logic



class StudentFeeDue(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='fee_due')
    academic_fee = models.ForeignKey(AcademicFee, on_delete=models.PROTECT)
    
    # Academic Math
    total_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Van Math
    van_fee = models.ForeignKey(VanFee, on_delete=models.PROTECT, null=True, blank=True)
    van_total_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    van_paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    van_due_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Academic calculations
        self.total_fee = self.academic_fee.annual_fee
        self.due_amount = self.total_fee - self.paid_amount

        # Van calculations
        if self.van_fee:
            self.van_total_fee = self.van_fee.annual_fee
            self.van_due_amount = self.van_total_fee - self.van_paid_amount
        else:
            self.van_total_fee = 0
            self.van_paid_amount = 0
            self.van_due_amount = 0

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Due Statement - {self.student.name}"
    

