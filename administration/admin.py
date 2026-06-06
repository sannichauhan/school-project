from django.contrib import admin
from django.utils.html import format_html
from .models import (
    AdmitCard,
    TransferCertificate,
    Attendance,
    AcademicFee,
    FeeReceipt,
    StudentFeeDue
)

# Register your models here.

@admin.register(AdmitCard)
class AdmitCardAdmin(admin.ModelAdmin):
    list_display = ['student__name', 'student__date_of_birth', 'student__roll_number', 'student__admission_class', 'student__father_name']


@admin.register(TransferCertificate)
class TransferCertificateAdmin(admin.ModelAdmin):

    list_display = [
        'student',
        'last_class_studied',
        'issue_date'
    ]

    search_fields = [
        'student__name',
    ]


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = (
        'attendance_date',
        'student',
        'student_class',
        'status'
    )

    list_filter = (
        'attendance_date',
        'student_class',
        'status'
    )

    search_fields = (
        'student__name',
        'student__roll_number'
    )

    date_hierarchy = 'attendance_date'


@admin.register(AcademicFee)
class AcademicFeeAdmin(admin.ModelAdmin):
    list_display = (
        'student_type',
        'class_group',
        'annual_fee',
        'first_installment',
        'second_installment',
        'third_installment',
    )

    list_filter = (
        'student_type',
        'class_group',
    )

    search_fields = (
        'student_type',
        'class_group',
    )

@admin.register(FeeReceipt)
class FeeReceiptAdmin(admin.ModelAdmin):

    list_display = (
        'receipt_no',
        'student',
        'installment',
        'amount',
        'payment_date'
    )

    search_fields = (
        'receipt_no',
        'student__name'
    )

@admin.register(StudentFeeDue)
class StudentFeeDueAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'total_fee',
        'paid_amount',
        'due_amount'
    )

    search_fields = (
        'student__name',
    )