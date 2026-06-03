from django.db import models
from django.utils import timezone
from student.models import Student, AcademicSession, Exam, StudentClass
from smart_selects.db_fields import ChainedForeignKey
import uuid
# Create your models here.

class FeeHead(models.Model):

    ADMISSION = 'admission'
    READMISSION = 'readmission'
    TUITION = 'tuition'
    EXAMINATION = 'examination'
    TRANSPORT = 'transport'
    MAINTENANCE = 'maintenance'
    FINE = 'fine'
    OTHER = 'other'

    FEE_TYPES = [
        (ADMISSION, 'Admission Fee'),
        (READMISSION, 'Readmission Fee'),
        (TUITION, 'Tuition Fee'),
        (EXAMINATION, 'Examination Fee'),
        (TRANSPORT, 'Transport Fee'),
        (MAINTENANCE, 'Maintenance Fee'),
        (FINE, 'Fine'),
        (OTHER, 'Other'),
    ]

    fee_type = models.CharField(max_length=50, choices=FEE_TYPES, unique=True)

    def __str__(self):
        return self.get_fee_type_display()

class FeeStructure(models.Model):

    student_class = models.ForeignKey(
        StudentClass,        
        on_delete=models.CASCADE
    )

    fee_head = models.ForeignKey(
        FeeHead,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.student_class} - {self.fee_head}"


class StudentFeeDue(models.Model):

    student_class = models.ForeignKey(
        StudentClass, 
        on_delete=models.PROTECT,
        null=True,
    )

    student_name =ChainedForeignKey(
        Student, 
        chained_field="student_class",
        chained_model_field="admission_class",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.PROTECT,
        related_name="fee_due_students"
    ) 

    fee_head = models.ForeignKey(
        FeeHead,
        on_delete=models.CASCADE
    )

    installment = models.CharField(max_length=50)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    fine = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    due_date = models.DateField()

    is_paid = models.BooleanField(default=False)

    def total_amount(self):
        return self.amount + self.fine

    def __str__(self):
        return f"{self.student_name} - {self.fee_head}"
    
class FeeReceipt(models.Model):

    receipt_no = models.CharField(max_length=50, unique=True, editable=False)

    student_class = models.ForeignKey(
        StudentClass, 
        on_delete=models.PROTECT,
        null=True,
    )

    student_name =ChainedForeignKey(
        Student, 
        chained_field="student_class",
        chained_model_field="admission_class",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.PROTECT,
        related_name="fee_receipt"
    )

    installment = models.CharField(max_length=50)

    date = models.DateField(auto_now_add=True)

    total_amount_received = models.DecimalField(max_digits=10, decimal_places=2)

    remarks = models.TextField(blank=True, null=True)

    @property
    def get_total_due(self):
        return float(self.installment) - float(self.total_amount_received)
    
    def save(self, *args, **kwargs):
        # Generate the receipt number ONLY if it hasn't been set yet (on creation)
        if not self.receipt_no:
            self.receipt_no = self.generate_receipt_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.receipt_no
    

    def generate_receipt_number(self):
        """
        Generates a unique receipt number. 
        Example output: REC-202605-A1B2C3D4
        """
        import datetime
        date_str = datetime.datetime.now().strftime("%Y%m")
        # Using a short UUID segment ensures uniqueness without complex database locks
        unique_suffix = uuid.uuid4().hex[:8].upper() 
        
        generated_no = f"REC-{date_str}-{unique_suffix}"
        
        # Double-check to make sure it doesn't miraculously collide
        while FeeReceipt.objects.filter(receipt_no=generated_no).exists():
            unique_suffix = uuid.uuid4().hex[:8].upper()
            generated_no = f"REC-{date_str}-{unique_suffix}"
            
        return generated_no
    
class ReceiptItem(models.Model):

    receipt = models.ForeignKey(
        FeeReceipt,
        on_delete=models.CASCADE,
        related_name='items'
    )

    fee_head = models.ForeignKey(
        FeeHead,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.receipt.receipt_no} - {self.fee_head}"
    
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
            'NAV CHETANA PUBLIC SCHOOL': '09591001108',
            'KAUSHALYA DEVI GIRLS NAV CHETANA PUBLIC J.H.S': '09591001109',
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