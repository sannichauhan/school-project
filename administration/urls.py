from django.urls import path, include
from . import views
from .views import admit_card_view, fee_receipt_view, create_tc_view, tc_list_view, tc_detail_view, take_attendance, attendance_report

urlpatterns = [
    path('', views.administration),
    path("chaining/", include("smart_selects.urls")),
    path('admit-card/', admit_card_view, name='admit-card'),
    path('fee-receipt/<int:pk>/', fee_receipt_view, name='fee-receipt'),
    path('transfer-certificate/create/', create_tc_view, name='tc-create'),
    path('transfer-certificate/list/', tc_list_view, name='tc-list'),
    path('transfer-certificate/<int:pk>/', tc_detail_view, name='tc-detail'),
    path('take-attendance/', take_attendance, name='take_attendance'),
    path('attendance-report/', attendance_report, name='attendance_report'),
]