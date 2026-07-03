# fee/services.py
from datetime import timedelta, timezone
import datetime
from decimal import Decimal

import fee
from .models import BaseFeeStructure, FeeLedger
from student.models import Student, AcademicSession, StudentEnrollment
from django.db import transaction
from django.db.models.signals import post_save
from django.db.models import Sum, F

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
            
def calculate_clean_installment(total_fee, total_installment = 3, standard_installment=2500):
    array_installments = []
    distribution =  total_fee - (standard_installment * (total_installment - 1))
    array_installments.append(distribution)
    rest_installments = (total_fee - distribution) / (total_installment - 1)
    for i in range(total_installment - 1):
        array_installments.append(rest_installments)
    return tuple(array_installments)

def create_fee_schedule_for_student(student, academic_year):

    transport = student.ledgers.filter(category='TRANSPORT')
    # Purane schedules ko duplicate hone se rokne ke liye safety check
    if FeeLedger.objects.filter(student=student, academic_year=academic_year).exclude(description__icontains='Carried Forward').exists() and transport:
        return
    elif student.conveyance_facility and FeeLedger.objects.filter(student=student, academic_year=academic_year).exclude(description__icontains='Carried Forward').exists():
        calculate_transport_fee(student, academic_year)
        return

    current_enrollment = StudentEnrollment.objects.filter(
            student=student, 
            is_active=True,
            academic_year__lt=academic_year
        ).order_by('-academic_year').first()
    
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

    base_fees = BaseFeeStructure.objects.filter(academic_year=academic_year, standard=student.current_class)
    total_academic_fee = sum(fee.total_amount for fee in base_fees)
    
    if student.current_class.serial > student.admission_class.serial:
        promotional_discount = student.current_class.promotional_discount or 0.0
        total_academic_fee = (total_academic_fee - promotional_discount)

    if total_academic_fee > 0:
        if student.fee_type == 'YEARLY':
            intervals = [0]
        elif student.fee_type == 'HALF_YEARLY':
            intervals = [0, 180]
        elif student.fee_type == "THRICE":
            intervals = [0, 120, 240]
        else: # QUARTERLY
            intervals = [0, 90, 180, 270]
        
        admission_class = student.admission_class
        current_class = student.current_class
        if admission_class and current_class and admission_class.serial < current_class.serial:
            # Agar student ko promote kiya gaya hai aur uska admission class current class se chhota hai, toh promotion discount apply karein
            promotional_discount = current_class.promotional_discount or 0.0
            total_academic_fee = (total_academic_fee - promotional_discount)
            
        installments = calculate_clean_installment(total_academic_fee, len(intervals))

        inst_count = len(intervals)

        for i in range(inst_count):
            FeeLedger.objects.create(
                student=student,
                academic_year=academic_year,
                installment_number=i + 1,
                category='ACADEMIC',
                description=f"Academic Fee - Installment {i + 1} ({student.get_fee_type_display()})",
                total_amount=installments[i],
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
            academic_year__lte=new_session
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
        create_fee_schedule_for_student(student, new_session)
        fee.signals.pre_save.connect(auto_ledger_for_promoted_student, sender=StudentEnrollment)
        # return new_enrollment
        
def create_ledger_for_student(student, new_academic_year, old_academic_year=None):
    total_due = get_student_due(student)
    deactivate_old_ledgers(student, old_academic_year)
    create_fee_schedule_for_student(student, new_academic_year)
    if total_due > 0:
        FeeLedger.objects.create(   
                student=student,
                academic_year=new_academic_year,
                installment_number=0,
                category='ACADEMIC',
                description=f"Carried Forward Dues",
                total_amount=total_due,
                due_date=datetime.datetime.now(),
                status='PENDING'
            )
def deactivate_old_ledgers(student, old_session):
    FeeLedger.objects.filter(student=student, academic_year=old_session).update(status='INACTIVE')
    
def get_student_due(student):
    total_due = FeeLedger.objects.filter(
        student=student,
        status__in=['PENDING', 'PARTIALLY_PAID'],
    ).aggregate(
        total=Sum(F('total_amount') - F('paid_amount'))
    )['total'] or 0

    return total_due

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
    # create_ledger_for_student(student, new_session)
    return new_enrollment

    