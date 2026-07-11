from decimal import Decimal, InvalidOperation
import secrets
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import FeeLedger, Transaction
from student.models import Student
from django.db.models import Sum, Max

# FIX: Yahan se @login_required hata diya hai, ab koi error nahi aayega
@transaction.atomic
def collect_fee_payment(ledger_id, amount_paid, payment_mode, transaction_id, user, receipt_number=None):
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
        collected_by=user,
        receipt_no=receipt_number
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
    
    academic_ledgers = FeeLedger.objects.filter(student=student, category='ACADEMIC', academic_year=student.session)
    transport_ledgers = FeeLedger.objects.filter(student=student, category='TRANSPORT', academic_year=student.session).order_by('due_date')
    
    total_due = sum(l.remaining_amount for l in FeeLedger.objects.filter(student=student, academic_year=student.session))
    total_paid = sum(l.paid_amount for l in FeeLedger.objects.filter(student=student, academic_year=student.session))

    context = {
        'student': student,
        'academic_ledgers': academic_ledgers,
        'transport_ledgers': transport_ledgers,
        'total_due': total_due,
        'total_paid': total_paid,
    }
    return render(request, 'dashboard.html', context)


@login_required
def fee_receipt_detail(request, receipt_no):
    transactions = Transaction.objects.filter(receipt_no=receipt_no).select_related(
        'ledger',
        'ledger__student__admission_class', 
        'ledger__academic_year', 
        'collected_by'
    )
    
    if not transactions.exists():
        # Fallback if no matching group record is found
        return render(request, '404.html', {'message': "Receipt nahi mili."})

    first_txn = transactions.first()
    student = first_txn.ledger.student
    
    grand_total = transactions.aggregate(total=Sum('amount_paid'))['total'] or 0

    context = {
        'receipt_no': receipt_no,
        'student': student,
        'payment_mode': first_txn.get_payment_mode_display(), 
        'transaction_id': first_txn.transaction_id,
        'payment_date': first_txn.payment_date,
        'collected_by': first_txn.collected_by,
        'transactions': transactions,
        'grand_total': grand_total,
    }
    
    return render(request, 'fee_receipt.html', context)


@login_required
def fee_receipt_list(request):
    """
    Displays a list of unique receipts grouped by receipt_no using 
    the exact fields from your Transaction model.
    """
    # Grouping records by receipt_no
    receipts = Transaction.objects.values('receipt_no').annotate(
        total_amount=Sum('amount_paid'),
        latest_payment_date=Max('payment_date'),
        
        mode_of_payment=Max('payment_mode'),
        tx_id=Max('transaction_id'),
        
        student_name=Max('ledger__student__name'),
        roll_number=Max('ledger__student__roll_number'),
        
        collected_by_user=Max('collected_by__username')
    ).order_by('-latest_payment_date')[:100]

    return render(request, 'fee_receipt_list.html', {'receipts': receipts})

@login_required
def checkout_fee_page(request):
    """
    Yeh view multiple ledgers ke liye checkout page render karta hai.
    """
    if request.method == 'POST':
        ledger_ids = request.POST.getlist('ledger_ids')
        ledgers = FeeLedger.objects.filter(id__in=ledger_ids, status__in=['PENDING', 'PARTIALLY_PAID'])
        
        if not ledgers.exists():
            messages.error(request, "No valid ledgers selected.")
            return redirect('student_fee_dashboard', student_id=request.user.id)  # Adjust as needed

        total_due = sum(l.remaining_amount for l in ledgers)
        total_paid = sum(l.paid_amount for l in ledgers)
        
        context = {
            'ledgers': ledgers,
            'total_due': total_due,
            'total_paid': total_paid,
            'student': ledgers.first().student if ledgers.exists() else None
        }
        return render(request, 'collect_fee.html', context)
    
    messages.error(request, "Invalid request method.")
    return redirect('student_fee_dashboard', student_id=request.user.id)  # Adjust as needed

@login_required
def collect_fee_multiple_ledgers(request):
    """
    Yeh view multiple ledgers ke liye payment process karta hai.
    """
    if request.method == 'POST':
        ledger_ids = request.POST.getlist('ledger_ids')
        amount_paid_raw = request.POST.get('amount_paid')
        payment_mode = request.POST.get('payment_mode')
        transaction_id = request.POST.get('transaction_id')
        try:
            if not amount_paid_raw:
                raise ValueError("Amount is mandatory.")
                
            amount_paid = Decimal(str(amount_paid_raw))
            ledgers = FeeLedger.objects.filter(id__in=ledger_ids, status__in=['PENDING', 'PARTIALLY_PAID'])
            
            total_due = sum(l.remaining_amount for l in ledgers)
            
            if amount_paid <= 0:
                messages.error(request, "Amount should be a positive value.")
                return redirect('checkout_fee_page')
                
            if amount_paid > total_due:
                messages.error(request, f"You can not pay more then outstanding amount : ({total_due}).")
                return redirect('checkout_fee_page')

            remaining_amount_to_pay = amount_paid
            
            student_id=ledgers.first().student.id
            unique_receipt_no = f"NCPS-{secrets.token_hex(4).upper()}"
            for ledger in ledgers:
                if remaining_amount_to_pay <= 0:
                    break
                
                pay_amount = min(ledger.remaining_amount, remaining_amount_to_pay)
                collect_fee_payment(
                    ledger_id=ledger.id,
                    amount_paid=pay_amount,
                    payment_mode=payment_mode,
                    transaction_id=transaction_id,
                    user=request.user,
                    receipt_number=unique_receipt_no
                )
                remaining_amount_to_pay -= pay_amount

            messages.success(request, f"Payment of ₹{amount_paid} successfully recorded across selected ledgers!")
            return redirect('student_fee_dashboard', student_id=student_id)

        except (InvalidOperation, ValueError) as e:
            messages.error(request, f"Error processing payment: Galat amount format ya koi technical error. ({str(e)})")
            return redirect('checkout_fee_page')

    messages.error(request, "Invalid request method.")
    return redirect('student_fee_dashboard', student_id=request.user.id)  # Adjust as needed