from django.urls import path
from . import views

urlpatterns = [
    path('<int:student_id>/', views.student_fee_dashboard, name='student_fee_dashboard'),
    path('ledger/pay/<int:ledger_id>/', views.collect_fee_view, name='collect_fee'),
    path('receipt/all/', views.fee_receipt_list, name='fee_receipt_list'),
    path('receipt/<int:transaction_id>/', views.fee_receipt_detail, name='fee_receipt_detail'),
]