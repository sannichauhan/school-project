from datetime import datetime

from django.db.models import Sum, F
from fee.models import FeeLedger
from student.models import AcademicSession


def _get_session_year(date_input: datetime) -> str:

    if date_input.month >= 4:
        start_year = date_input.year
    else:
        start_year = date_input.year - 1
        
    end_year = start_year + 1
    return f"{start_year}-{end_year}"


def get_current_academic_total_fees_and_due():
    session = _get_session_year(datetime.now())
    active_session = AcademicSession.objects.filter(name=session, is_active=True).first()
    if not active_session:
        return 0, 0

    # 1. Calculate total scheduled fees
    total_fees = FeeLedger.objects.filter(academic_year=active_session).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # 2. Calculate remaining due by subtracting paid_amount from total_amount dynamically
    total_due = FeeLedger.objects.filter(
        academic_year=active_session, 
        status__in=['PENDING', 'PARTIALLY_PAID']
    ).aggregate(
        total=Sum(F('total_amount') - F('paid_amount'))
    )['total'] or 0

    return total_fees, total_due