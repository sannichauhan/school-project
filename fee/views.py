from decimal import Decimal

from django.shortcuts import render

# Create your views here.
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import FeeLedger, Transaction
from django.contrib.auth.decorators import login_required

@login_required
@transaction.atomic
def collect_fee_payment(ledger_id, amount_paid, payment_mode, transaction_id, user):
    ledger = get_object_or_404(FeeLedger, id=ledger_id)
    
    if amount_paid > ledger.remaining_amount:
        raise ValueError(f"Paying amount is greater than due amount ({ledger.remaining_amount})")

    txn = Transaction.objects.create(
        ledger=ledger,
        amount_paid=amount_paid,
        payment_mode=payment_mode,
        transaction_id=transaction_id,
        collected_by=user
    )
    
    # 2. Update Ledger Status
    ledger.paid_amount += Decimal(amount_paid)
    
    if ledger.paid_amount == ledger.total_amount:
        ledger.status = 'PAID'
    elif ledger.paid_amount > 0:
        ledger.status = 'PARTIALLY_PAID'
        
    ledger.save()
    return txn


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from .models import FeeLedger, Transaction
from student.models import Student

@login_required
def student_fee_dashboard(request, student_id):
    """
    Direct student profile field mappings ke sath updated dashboard view
    """
    student = get_object_or_404(Student, id=student_id)
    
    academic_ledgers = FeeLedger.objects.filter(student=student, category='ACADEMIC').order_by('due_date')
    transport_ledgers = FeeLedger.objects.filter(student=student, category='TRANSPORT').order_by('due_date')
    
    total_due = sum(l.remaining_amount for l in FeeLedger.objects.filter(student=student))
    total_paid = sum(l.paid_amount for l in FeeLedger.objects.filter(student=student))

    context = {
        'student': student,
        'academic_ledgers': academic_ledgers,
        'transport_ledgers': transport_ledgers,
        'total_due': total_due,
        'total_paid': total_paid,
    }
    return render(request, 'dashboard.html', context)


# fee/views.py me collect_fee_view ko isse replace karein:

def collect_fee_view(request, ledger_id):
    """
    Specific installment par payment apply karne ka view (Direct Student Mapping).
    """
    ledger = get_object_or_404(FeeLedger, id=ledger_id)
    
    student_id = ledger.student.id

    if request.method == 'POST':
        amount_paid = request.POST.get('amount_paid')
        payment_mode = request.POST.get('payment_mode')
        transaction_id = request.POST.get('transaction_id')

        try:
            amount_paid = float(amount_paid)
            
            if amount_paid <= 0:
                messages.error(request, "Amount 0 se zyada hona chahiye.")
                return redirect('collect_fee', ledger_id=ledger.id)
                
            if amount_paid > ledger.remaining_amount:
                messages.error(request, f"Aap outstanding amount ({ledger.remaining_amount}) se zyada pay nahi kar sakte.")
                return redirect('collect_fee', ledger_id=ledger.id)

            with transaction.atomic():
                Transaction.objects.create(
                    ledger=ledger,
                    amount_paid=amount_paid,
                    payment_mode=payment_mode,
                    transaction_id=transaction_id if transaction_id else None,
                    collected_by=request.user if request.user.is_authenticated else None
                )
                
                # Update ledger state
                ledger.paid_amount += type(ledger.paid_amount)(amount_paid)
                if ledger.paid_amount == ledger.total_amount:
                    ledger.status = 'PAID'
                else:
                    ledger.status = 'PARTIALLY_PAID'
                ledger.save()

            messages.success(request, f"Payment of ₹{amount_paid} successfully recorded!")
            return redirect('student_fee_dashboard', student_id=student_id)

        except Exception as e:
            messages.error(request, f"Error processing payment: {str(e)}")
            return redirect('collect_fee', ledger_id=ledger.id)

    return render(request, 'collect_fee.html', {'ledger': ledger})