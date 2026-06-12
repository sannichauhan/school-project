# fee/admin.py
from django.contrib import admin
from .models import FeeHead, BaseFeeStructure, TransportRoute, FeeLedger, Transaction
from student.models import TransportRoute


@admin.register(FeeHead)
class FeeHeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(TransportRoute)
class TransportRouteAdmin(admin.ModelAdmin):
    list_display = ('route_name', 'yearly_fee')

@admin.register(BaseFeeStructure)
class BaseFeeStructureAdmin(admin.ModelAdmin): list_display = ('academic_year', 'standard', 'fee_head', 'total_amount')

@admin.register(FeeLedger)
class FeeLedgerAdmin(admin.ModelAdmin): list_display = ('student', 'category', 'description', 'total_amount', 'status')