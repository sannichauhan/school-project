from django.db import models
from django.utils import timezone
from student.models import Student, AcademicSession, Exam, StudentClass
from smart_selects.db_fields import ChainedForeignKey
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