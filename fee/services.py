from datetime import timedelta
from decimal import Decimal
from .models import BaseFeeStructure, FeeLedger, StudentFeeAllocation

def create_fee_schedule_for_student(student, academic_year):
    """
    Student ki class agar kisi Fee Structure ke range (class_from to class_to) me aati hai,
    toh uske mutabik fixed 3 installments (Inst 1 dynamic, Inst 2 & 3 = ₹2500) generate karna.
    """
    # 1. Safe Re-generation Mode: Purane saare ledgers ko pehle clear (delete) karein
    # Taaki signal chalte hi naye rules ke mutabik fresh data generate ho sake.
    FeeLedger.objects.filter(student=student, academic_year=academic_year).delete()

    # 2. Get active allocation detail
    allocation = StudentFeeAllocation.objects.filter(student=student, academic_year=academic_year).first()
    if not allocation:
        return

    # 3. Dynamic Range Check for Academic Fee
    all_structures = BaseFeeStructure.objects.filter(academic_year=academic_year)
    
    # Filter by admission type (NEW vs OLD)
    if allocation.admission_type == 'OLD':
        all_structures = all_structures.filter(is_new_student_only=False)
    else:
        all_structures = all_structures.filter(is_new_student_only=True)

    total_academic_fee = Decimal('0.00')
    student_class_id = student.current_class.id

    # SINGLE CLEAN LOOP: Range check logic
    for structure in all_structures:
        min_id = min(structure.class_from.id, structure.class_to.id)
        max_id = max(structure.class_from.id, structure.class_to.id)
        
        # Agar student ki class range ke andar fall karti hai
        if min_id <= student_class_id <= max_id:
            total_academic_fee = Decimal(str(structure.total_amount))
            break # Match milte hi loop se bahar niklein

    # Generate Academic Ledger entries if fee found
    if total_academic_fee > 0:
        if allocation.fee_type == 'YEARLY':
            intervals = [0]
            amounts = [total_academic_fee]
            
        elif allocation.fee_type == 'HALF_YEARLY':
            intervals = [0, 180]
            half_amount = (total_academic_fee / 2).quantize(Decimal('0.01'))
            amounts = [half_amount, total_academic_fee - half_amount]
            
        else:  # TERM (3 Installments - Jaisa aapki school board slips me hai)
            intervals = [0, 90, 180]
            fixed_inst_value = Decimal('2500.00')
            
            # Agar fee criteria fixed structure se badi hai (Jaise 7500, 8000, 10250)
            if total_academic_fee > (fixed_inst_value * 2):
                inst2_amount = fixed_inst_value
                inst3_amount = fixed_inst_value
                # Bacha hua extra fraction premium amount 1st installment me automatic chala jayega
                inst1_amount = total_academic_fee - (inst2_amount + inst3_amount)
            else:
                # Safe fallback configuration
                inst1_amount = (total_academic_fee / 3).quantize(Decimal('0.01'))
                inst2_amount = inst1_amount
                inst3_amount = total_academic_fee - (inst1_amount + inst2_amount)
                
            amounts = [inst1_amount, inst2_amount, inst3_amount]

        # Save to Database
        for i in range(len(intervals)):
            FeeLedger.objects.create(
                student=student,
                academic_year=academic_year,
                installment_number=i + 1,
                category='ACADEMIC',
                description=f"Academic Fee - Installment {i + 1} ({allocation.get_fee_type_display()})",
                total_amount=amounts[i],
                due_date=academic_year.start_date + timedelta(days=intervals[i])
            )

    # 4. Transport Fee Setup
    if hasattr(student, 'conveyance_facility') and student.conveyance_facility and allocation.transport_route:
        transport_total = allocation.transport_route.yearly_fee
        
        # Default fallback to 1 installment if not selected to prevent dashboard errors
        t_inst_type = allocation.transport_installment_type or '1_INSTALLMENT'
        t_intervals = [0] if t_inst_type == '1_INSTALLMENT' else [0, 180]
        t_inst_count = len(t_intervals)
        
        transport_inst_amount = (Decimal(transport_total) / t_inst_count).quantize(Decimal('0.01'))
        
        for j in range(t_inst_count):
            if j == t_inst_count - 1:
                t_amount_to_charge = Decimal(transport_total) - (transport_inst_amount * (t_inst_count - 1))
            else:
                t_amount_to_charge = transport_inst_amount

            FeeLedger.objects.create(
                student=student,
                academic_year=academic_year,
                installment_number=j + 1,
                category='TRANSPORT',
                description=f"Transport Fee - Installment {j + 1}",
                total_amount=t_amount_to_charge,
                due_date=academic_year.start_date + timedelta(days=t_intervals[j])
            )