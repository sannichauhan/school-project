from decimal import Decimal, InvalidOperation
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import FeeLedger, Transaction
from student.models import Student

# FIX: Yahan se @login_required hata diya hai, ab koi error nahi aayega
@transaction.atomic
def collect_fee_payment(ledger_id, amount_paid, payment_mode, transaction_id, user):
    """
    Yeh ek UTILITY function hai (Yeh direct view nahi hai, isme 'request' pass nahi karna hai).
    """
    ledger = get_object_or_404(FeeLedger, id=ledger_id)
    amount_paid_decimal = Decimal(str(amount_paid))
    
    if amount_paid_decimal > ledger.remaining_amount:
        raise ValueError(f"Paying amount is greater than due amount ({ledger.remaining_amount})")

    # 1. Create Transaction
    txn = Transaction.objects.create(
        ledger=ledger,
        amount_paid=amount_paid_decimal,
        payment_mode=payment_mode,
        transaction_id=transaction_id if transaction_id else None,
        collected_by=user
    )
    
    # 2. Update Ledger
    ledger.paid_amount += amount_paid_decimal
    if ledger.paid_amount == ledger.total_amount:
        ledger.status = 'PAID'
    elif ledger.paid_amount > 0:
        ledger.status = 'PARTIALLY_PAID'
        
    ledger.save()
    return txn


@login_required
def collect_fee_view(request, ledger_id):
    """
    Yeh ACTUAL VIEW hai jise URL point karta hai.
    """
    ledger = get_object_or_404(FeeLedger, id=ledger_id)
    student_id = ledger.student.id

    if request.method == 'POST':
        amount_paid_raw = request.POST.get('amount_paid')
        payment_mode = request.POST.get('payment_mode')
        transaction_id = request.POST.get('transaction_id')

        try:
            # 1. Sabse pehle input ko safely Decimal me convert karein
            if not amount_paid_raw:
                raise ValueError("Amount daalna zaroori hai.")
                
            amount_paid = Decimal(str(amount_paid_raw))
            
            # 2. Validation Checks
            if amount_paid <= 0:
                messages.error(request, "Amount 0 se zyada hona chahiye.")
                return redirect('collect_fee', ledger_id=ledger.id)
                
            if amount_paid > ledger.remaining_amount:
                messages.error(request, f"Aap outstanding amount ({ledger.remaining_amount}) se zyada pay nahi kar sakte.")
                return redirect('collect_fee', ledger_id=ledger.id)

            # 3. Agar sab sahi hai, toh utility function call karein
            collect_fee_payment(
                ledger_id=ledger.id,
                amount_paid=amount_paid,
                payment_mode=payment_mode,
                transaction_id=transaction_id,
                user=request.user
            )

            messages.success(request, f"Payment of ₹{amount_paid} successfully recorded!")
            return redirect('student_fee_dashboard', student_id=student_id)

        except (InvalidOperation, ValueError) as e:
            # Ab yahan 'amount_paid' ke crash hone ka jhanjhat hi khatam
            messages.error(request, f"Error processing payment: Galat amount format ya koi technical error. ({str(e)})")
            return redirect('collect_fee', ledger_id=ledger.id)

    return render(request, 'collect_fee.html', {'ledger': ledger})


@login_required
def student_fee_dashboard(request, student_id):
    """
    Student profile metrics dashboard visualization engine views mapping.
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


@login_required
def fee_receipt_detail(request, transaction_id):
    """
    Renders the beautiful print-ready official fee receipt for a specific transaction.
    """
    # Performance Optimization: Using select_related to load student, class and collector in 1 query
    transaction = get_object_or_404(
        Transaction.objects.select_related(
            'ledger',
            'ledger__student__admission_class', 
            'ledger__academic_year', 
            'collected_by'
        ), 
        id=transaction_id
    )
    
    return render(request, 'fee_receipt.html', {'transaction': transaction})


@login_required
def fee_receipt_list(request):
    """
    Displays a historical table log of all payment transactions collected across the institution.
    """
    
    transactions = Transaction.objects.select_related(
        'ledger__student', 
        'collected_by'
    ).order_by('-payment_date')[:100]
    
    # Is return statement ke aage bhi exact 4 spaces ya 1 tab hona chahiye
    return render(request, 'fee_receipt_list.html', {'transactions': transactions})