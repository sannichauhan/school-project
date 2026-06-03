from django.contrib import admin
from django.utils.html import format_html
from .models import (
    FeeHead,
    FeeStructure,
    StudentFeeDue,
    FeeReceipt,
    ReceiptItem,
    AdmitCard,
    TransferCertificate,
    Attendance
)

# Register your models here.
@admin.register(FeeHead)
class FeeHeadAdmin(admin.ModelAdmin):

    list_display = ('id', 'fee_type')

    search_fields = ('fee_type',)

class ReceiptItemInline(admin.TabularInline):

    model = ReceiptItem

    extra = 1

@admin.register(FeeReceipt)
class FeeReceiptAdmin(admin.ModelAdmin):

    list_display = (
        'receipt_no',
        'student_name',
        'student_class',
        'installment',
        'date',
        'total_amount_display'
    )

    list_filter = ('installment', 'date')

    search_fields = (
        'receipt_no',
        'student_name',
        'student_class'
    )

    inlines = [ReceiptItemInline]

    @admin.display(description='Total Amount')
    def total_amount_display(self, obj):
        return format_html('<b>₹{}</b>', obj.total_amount_received)
    
@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):

    list_display = (
        'student_class',
        'fee_head',
        'amount_display'
    )

    list_filter = ('student_class', 'fee_head')

    search_fields = (
        'student_class',
        'fee_head__fee_type'
    )

    @admin.display(description='Amount')
    def amount_display(self, obj):
        return format_html('<b>₹{}</b>', obj.amount)
    
@admin.register(StudentFeeDue)
class StudentFeeDueAdmin(admin.ModelAdmin):

    list_display = (
        'student_name',
        'student_class',
        'fee_head',
        'installment',
        'amount',
        'fine',
        'due_date',
        'is_paid'
    )

    list_filter = (
        'student_class',
        'is_paid',
        'fee_head'
    )

    search_fields = (
        'student_name',
        'student_class'
    )

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