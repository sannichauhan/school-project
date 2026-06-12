# fee/services.py
from datetime import timedelta
from decimal import Decimal
from .models import BaseFeeStructure, FeeLedger
from student.models import Student, AcademicSession

def create_fee_schedule_for_student(student, academic_year):
    """
    Kee bhi student ke liye specified Academic Year ka poora bill table ready karna.
    """
    # Purane schedules ko duplicate hone se rokne ke liye safety check
    if FeeLedger.objects.filter(student=student, academic_year=academic_year).exists():
        return

    base_fees = BaseFeeStructure.objects.filter(academic_year=academic_year, standard=student.current_class)
    total_academic_fee = sum(fee.total_amount for fee in base_fees)

    if total_academic_fee > 0:
        if student.fee_type == 'YEARLY':
            intervals = [0]
        elif student.fee_type == 'HALF_YEARLY':
            intervals = [0, 180]
        else: # QUARTERLY
            intervals = [0, 90, 180, 270]

        inst_count = len(intervals)
        academic_inst_amount = Decimal(total_academic_fee) / inst_count

        for i in range(inst_count):
            FeeLedger.objects.create(
                student=student,
                academic_year=academic_year,
                installment_number=i + 1,
                category='ACADEMIC',
                description=f"Academic Fee - Installment {i + 1} ({student.get_fee_type_display()})",
                total_amount=academic_inst_amount,
                due_date=academic_year.start_date + timedelta(days=intervals[i])
            )

    # 2. Transport Fee Allocation
    if student.conveyance_facility and student.transport_route:
        transport_total = student.transport_route.yearly_fee
        t_intervals = [0] if student.transport_installment_type == '1_INSTALLMENT' else [0, 180]
        
        transport_inst_amount = Decimal(transport_total) / len(t_intervals)
        
        for j in range(len(t_intervals)):
            FeeLedger.objects.create(
                student=student,
                academic_year=academic_year,
                installment_number=j + 1,
                category='TRANSPORT',
                description=f"Transport Fee - Installment {j + 1}",
                total_amount=transport_inst_amount,
                due_date=academic_year.start_date + timedelta(days=t_intervals[j])
            )