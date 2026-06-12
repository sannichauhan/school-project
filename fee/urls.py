from django.urls import path
from . import views

urlpatterns = [
    path('<int:student_id>/', views.student_fee_dashboard, name='student_fee_dashboard'),
    path('ledger/<int:ledger_id>/pay/', views.collect_fee_view, name='collect_fee'),
]