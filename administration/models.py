from django.db import models
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
    

class FeeReceipt(models.Model):

    INSTALLMENT_CHOICES = (
        ('FIRST', '1st Installment'),
        ('SECOND', '2nd Installment'),
        ('THIRD', '3rd Installment'),
    )

    receipt_no = models.CharField(max_length=50, unique=True, editable=False)

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
        related_name="fee_receipt",
        null=True,
        blank=True
    )

    academic_fee = models.ForeignKey(
        AcademicFee,
        on_delete=models.PROTECT
    )

    installment = models.CharField(
        max_length=10,
        choices=INSTALLMENT_CHOICES
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Actual Amount Paid"
    )
    

    payment_date = models.DateField()

    payment_mode = models.CharField(
        max_length=20,
        default='Cash'
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ['student', 'installment']

    def __str__(self):
        return self.receipt_no
    
    def save(self, *args, **kwargs):

        # Auto Receipt Number
        if not self.receipt_no:

            today = timezone.now()

            last_receipt = FeeReceipt.objects.filter(
                created_at__year=today.year
            ).order_by('-id').first()

            if last_receipt:
                try:
                    last_no = int(last_receipt.receipt_no.split('-')[-1])
                except:
                    last_no = 0
            else:
                last_no = 0

            self.receipt_no = (
                f"RCPT-{today.year}-{last_no + 1:04d}"
            )

        # Auto Installment Amount
        if self.installment == 'FIRST':
            self.amount = self.academic_fee.first_installment

        elif self.installment == 'SECOND':
            self.amount = self.academic_fee.second_installment

        elif self.installment == 'THIRD':
            self.amount = self.academic_fee.third_installment

        super().save(*args, **kwargs)

        # Update Fee Due
        fee_due, created = StudentFeeDue.objects.get_or_create(
            student=self.student,
            defaults={
                'academic_fee': self.academic_fee
            }
        )

        total_paid = FeeReceipt.objects.filter(
            student=self.student
        ).aggregate(
            total=Sum('paid_amount')
        )['total'] or 0

        fee_due.paid_amount = total_paid
        fee_due.save()



class StudentFeeDue(models.Model):

    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name='fee_due'
    )

    academic_fee = models.ForeignKey(
        AcademicFee,
        on_delete=models.PROTECT
    )

    total_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    due_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self, *args, **kwargs):

        self.total_fee = self.academic_fee.annual_fee
        self.due_amount = self.total_fee - self.paid_amount

        super().save(*args, **kwargs)

    def __str__(self):
        return self.student.name
    

