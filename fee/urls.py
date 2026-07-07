from django.urls import path
from . import views

urlpatterns = [
    path('<int:student_id>/', views.student_fee_dashboard, name='student_fee_dashboard'),
    path('ledger/pay/<int:ledger_id>/', views.collect_fee_view, name='collect_fee'),
    path('receipt/all/', views.fee_receipt_list, name='fee_receipt_list'),
    path('receipt/<str:receipt_no>/', views.fee_receipt_detail, name='fee_receipt_detail'),
    path('checkout/', views.checkout_fee_page, name='checkout_fee_page'),
    path('collect-multiple/', views.collect_fee_multiple_ledgers, name='collect_multiple_fees'),
]