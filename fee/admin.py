from django.contrib import admin
from .models import FeeHead, BaseFeeStructure, StudentFeeAllocation, FeeLedger, Transaction
from student.models import TransportRoute

@admin.register(FeeHead)
class FeeHeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(TransportRoute)
class TransportRouteAdmin(admin.ModelAdmin):
    list_display = ('route_name', 'yearly_fee')
    search_fields = ('route_name',)

@admin.register(BaseFeeStructure)
class BaseFeeStructureAdmin(admin.ModelAdmin): 
    list_display = ('academic_year', 'display_range', 'fee_head', 'total_amount', 'is_new_student_only')
    list_filter = ('academic_year', 'is_new_student_only')

    def display_range(self, obj):
        # Safe lookup using if-else condition
        from_class = obj.class_from.name if obj.class_from else "N/A"
        to_class = obj.class_to.name if obj.class_to else "N/A"
        return f"{from_class} to {to_class}"
    
    display_range.short_description = "Class Range"

@admin.register(StudentFeeAllocation)
class StudentFeeAllocationAdmin(admin.ModelAdmin):
    list_display = ('student', 'academic_year', 'admission_type', 'fee_type', 'transport_route')
    list_filter = ('academic_year', 'admission_type', 'fee_type')
    search_fields = ('student__student_name',)

@admin.register(FeeLedger)
class FeeLedgerAdmin(admin.ModelAdmin): 
    list_display = ('student', 'category', 'installment_number', 'description', 'total_amount', 'paid_amount', 'status', 'due_date')
    list_filter = ('status', 'category', 'academic_year')
    search_fields = ('student__student_name', 'description')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('ledger', 'amount_paid', 'payment_mode', 'transaction_id', 'payment_date', 'collected_by')
    list_filter = ('payment_mode', 'payment_date')
    search_fields = ('transaction_id', 'ledger__student__student_name')