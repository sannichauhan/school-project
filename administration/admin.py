from django.contrib import admin
from django.utils.html import format_html
from .models import (
    AdmitCard,
    TransferCertificate,
    Attendance
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