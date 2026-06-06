from django.urls import path, include
from . import views
from .views import admit_card_view, create_tc_view, tc_list_view, tc_detail_view, take_attendance, attendance_report, fee_receipt_create, fee_receipt_list, fee_receipt_details, get_installment_amount


urlpatterns = [
    path('', views.administration),
    path("chaining/", include("smart_selects.urls")),
    path('admit-card/', admit_card_view, name='admit-card'),
    path('transfer-certificate/create/', create_tc_view, name='tc-create'),
    path('transfer-certificate/list/', tc_list_view, name='tc-list'),
    path('transfer-certificate/<int:pk>/', tc_detail_view, name='tc-detail'),
    path('take-attendance/', take_attendance, name='take_attendance'),
    path('attendance-report/', attendance_report, name='attendance_report'),
    path('academic-fee-add/', views.academic_fee_create, name='academic-fee-add'),
    path('academic-fee-list/', views.academic_fee_list, name='academic-fee-list'),
    path('fee-receipt-create/', fee_receipt_create, name='fee_receipt_create'),
    path('fee-receipt-list/', fee_receipt_list, name='fee_receipt_list'),
    path('fee-receipt-details/<int:pk>/', fee_receipt_details, name='fee_receipt_details'),
    path('installment-amount/', get_installment_amount, name='get_installment_amount'),    
]