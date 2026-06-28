# fee/services.py
from datetime import timedelta, timezone
import datetime
from decimal import Decimal

import fee
from .models import BaseFeeStructure, FeeLedger
from student.models import Student, AcademicSession, StudentEnrollment
from django.db import transaction
from django.db.models.signals import post_save

def calculate_transport_fee(student: Student, academic_year):
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
def create_fee_schedule_for_student(student, academic_year):
    """
    Kee bhi student ke liye specified Academic Year ka poora bill table ready karna.
    """
    transport = student.ledgers.filter(category='TRANSPORT')
    # Purane schedules ko duplicate hone se rokne ke liye safety check
    if FeeLedger.objects.filter(student=student, academic_year=academic_year).exists() and transport:
        return
    elif student.conveyance_facility and FeeLedger.objects.filter(student=student, academic_year=academic_year).exists():
        calculate_transport_fee(student, academic_year)
        return


    base_fees = BaseFeeStructure.objects.filter(academic_year=academic_year, standard=student.current_class)
    total_academic_fee = sum(fee.total_amount for fee in base_fees)

    if total_academic_fee > 0:
        if student.fee_type == 'YEARLY':
            intervals = [0]
        elif student.fee_type == 'HALF_YEARLY':
            intervals = [0, 180]
        elif student.fee_type == "THRICE":
            intervals = [0, 120, 240]
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
    calculate_transport_fee(student, academic_year)
    
            
def promote_student_with_ledger(student, target_class, new_session):
    """
    Promotes a student to the next class and carries forward balances,
    safely handling signal structures to prevent recursion.
    """
    # Import your receiver here to avoid circular imports
    from fee.signals import auto_ledger_for_promoted_student

    with transaction.atomic():
        current_enrollment = StudentEnrollment.objects.filter(
            student=student, 
            is_active=True,
            to_class__serial__lte=target_class.serial
        ).first()
        fee.signals.pre_save.disconnect(auto_ledger_for_promoted_student, sender=StudentEnrollment)
        previous_dues = 0.00
        if current_enrollment:
            old_session = current_enrollment.academic_year
            unpaid_ledgers = FeeLedger.objects.filter(
                student=student,
                academic_year=old_session,
                status__in=['PENDING', 'PARTIALLY_PAID']
            )
            for ledger in unpaid_ledgers:
                previous_dues += float(ledger.remaining_amount)
            
            current_enrollment.is_active = False
            current_enrollment.save()
            

        # Handle your ledger carry-forward logic safely below
        if previous_dues > 0:
            FeeLedger.objects.create(   
                student=student,
                academic_year=new_session,
                installment_number=0,
                category='ACADEMIC',
                description=f"Carried Forward Dues",
                total_amount=previous_dues,
                due_date=datetime.datetime.now(),
                status='PENDING'
            )
        fee.signals.pre_save.connect(auto_ledger_for_promoted_student, sender=StudentEnrollment)
        # return new_enrollment
        
def brand_new_enrollment(student, target_class, new_session):
    """
    Creates a new enrollment for the student in the target class and session.
    """
    new_enrollment = StudentEnrollment.objects.create(
        student=student,
        from_class=student.current_class,
        to_class=target_class,
        academic_year=new_session,
        is_active=True,
        status='ACTIVE'
    )
    return new_enrollment