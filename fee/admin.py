from django.contrib import admin
from .models import FeeHead, BaseFeeStructure, StudentFeeAllocation, FeeLedger, Transaction
from student.models import TransportRoute
from .models import FeeInstallmentStructure

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
    list_display = ('academic_year', 'standard', 'fee_head', 'total_amount')
    list_filter = ('academic_year',)

@admin.register(StudentFeeAllocation)
class StudentFeeAllocationAdmin(admin.ModelAdmin):
    list_display = ('student', 'academic_year', 'fee_type', 'transport_route')
    list_filter = ('academic_year', 'fee_type')
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




# 1. Inline class taaki saari installments ek hi page par tabular form me dikhein
class FeeInstallmentStructureInline(admin.TabularInline):
    model = FeeInstallmentStructure
    extra = 3  # By default 3 khali rows dikhayega naya data entry karne ke liye
    min_num = 1
    ordering = ('installment_number',)

# 2. Main Admin configuration (Optional: Agar aap alag se bhi register karna chahein)
@admin.register(FeeInstallmentStructure)
class FeeInstallmentStructureAdmin(admin.ModelAdmin):
    list_display = ('academic_year', 'standard', 'installment_number', 'amount', 'days_from_start')
    list_filter = ('academic_year', 'standard')
    search_fields = ('standard',)
    ordering = ('academic_year', 'standard', 'installment_number')