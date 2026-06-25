from django.db import models
import uuid
from decimal import Decimal
from django.contrib.auth.models import User
from student.models import Student, AcademicSession, StudentClass, TransportRoute
    

class FeeHead(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

# fee/models.py me sirf BaseFeeStructure model ko isse replace karein:

# Final Final State of the Model
class BaseFeeStructure(models.Model):
    academic_year = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    
    # standard field is now completely removed
    standard = models.ForeignKey(StudentClass, on_delete=models.CASCADE, related_name='fees', null=True, blank=True)
    fee_head = models.ForeignKey(FeeHead, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.fee_head.name}"

class StudentFeeAllocation(models.Model):
    FEE_TYPE_CHOICES = [
        ('TERM', 'Three Installments'),
        ('HALF_YEARLY', 'Half Yearly'),
        ('YEARLY', 'Yearly'),
    ]
    TRANSPORT_INSTALLMENT_CHOICES = [
        ('1_INSTALLMENT', 'Single Installment'),
        ('2_INSTALLMENT', 'Two Installments'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES)
    transport_route = models.ForeignKey(TransportRoute, on_delete=models.SET_NULL, null=True, blank=True)
    transport_installment_type = models.CharField(max_length=20, choices=TRANSPORT_INSTALLMENT_CHOICES, null=True, blank=True)

    class Meta:
        unique_together = ('student', 'academic_year')

    def __str__(self):
        return f"{self.student} - {self.academic_year}"

class FeeLedger(models.Model):
    STATUS_CHOICES = [('PENDING', 'Pending'), ('PARTIALLY_PAID', 'Partially Paid'), ('PAID', 'Paid')]
    CATEGORY_CHOICES = [('ACADEMIC', 'Academic Fee'), ('TRANSPORT', 'Transport Fee')]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='ledgers', null=True, blank=True)
    academic_year = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, null=True, blank=True)
    installment_number = models.PositiveIntegerField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='ACADEMIC')
    description = models.CharField(max_length=100)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    @property
    def remaining_amount(self):
        if self.total_amount is None: return Decimal('0.00')
        paid = self.paid_amount if self.paid_amount is not None else Decimal('0.00')
        return self.total_amount - paid

class Transaction(models.Model):
    PAYMENT_MODES = [('CASH', 'Cash'), ('ONLINE', 'Online / UPI'), ('CHEQUE', 'Cheque')]
    
    ledger = models.ForeignKey(FeeLedger, on_delete=models.CASCADE, related_name='transactions')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODES)
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True) # blank=True, null=True zaroori hai
    payment_date = models.DateTimeField(auto_now_add=True)
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        # Agar transaction_id pehle se nahi h (matlab naya record hai)
        if not self.transaction_id:
            # unique_id generate karein (Aap iska format change kar sakte hain)
            # Yeh "TXN-" ke sath ek 8-character ka unique random hex code jod dega
            self.transaction_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
            
            # Agar aapko check karna ho ki kahin yeh ID pehle se exist to nahi karti:
            while Transaction.objects.filter(transaction_id=self.transaction_id).exists():
                self.transaction_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"
                
        super(Transaction, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_id} - {self.amount_paid}"