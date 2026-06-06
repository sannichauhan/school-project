from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib import messages
from .models import AdmitCard, TransferCertificate, Attendance, AcademicFee, FeeReceipt, StudentFeeDue
from .forms import TransferCertificateForm, AcademicFeeForm, FeeReceiptForm
from student.models import StudentClass, Student

def administration(request):
    return HttpResponse("Hello")       

def admit_card_view(request):

    class_id = request.GET.get("class_id")

    admit_cards = AdmitCard.objects.select_related(
        'student',
        'student__admission_class',
        'session',
        'exam_type'
    )

    if class_id:
        admit_cards = admit_cards.filter(
            student__admission_class_id=class_id
        )

    admit_cards = admit_cards.order_by(
        'student__admission_class__name',
        'student__name'
    )

    return render(
        request,
        'admit-card.html',
        {
            'admit_cards': admit_cards
        }
    )





def create_tc_view(request):

    if request.method == 'POST':

        form = TransferCertificateForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('tc-list')

    else:

        form = TransferCertificateForm()

    return render(request, 'create_tc.html', {
        'form': form
    })


def tc_list_view(request):

    certificates = TransferCertificate.objects.select_related(
        'student'
    ).all()

    return render(request, 'tc_list.html', {
        'certificates': certificates
    })


def tc_detail_view(request, pk):

    tc = get_object_or_404(
        TransferCertificate,
        pk=pk
    )


    return render(request, 'tc_detail.html', {
        'tc': tc
    })

def take_attendance(request):

    classes = StudentClass.objects.all()

    selected_class = None
    students = []

    class_id = request.GET.get('class_id')

    if class_id:
        selected_class = StudentClass.objects.get(id=class_id)
        students = Student.objects.filter(
            admission_class=selected_class
        )

    if request.method == 'POST':

        class_id = request.POST.get('class_id')
        attendance_date = request.POST.get('attendance_date')

        selected_class = StudentClass.objects.get(id=class_id)

        students = Student.objects.filter(
            admission_class=selected_class
        )

        for student in students:

            status = request.POST.get(
                f"student_{student.id}"
            )

            Attendance.objects.update_or_create(
                student=student,
                attendance_date=attendance_date,
                defaults={
                    'student_class': selected_class,
                    'status': status
                }
            )

        messages.success(
            request,
            "Attendance saved successfully."
        )

        return redirect('take_attendance')

    context = {
        'classes': classes,
        'students': students,
        'selected_class': selected_class,
        'today': date.today()
    }

    return render(
        request,
        'take_attendance.html',
        context
    )

def attendance_report(request):

    records = Attendance.objects.select_related(
        'student',
        'student_class'
    )

    return render(
        request,
        'attendance_report.html',
        {'records': records}
    )

def academic_fee_create(request):

    form = AcademicFeeForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('academic-fee-list')

    return render(
        request,
        'academic_fee_form.html',
        {'form': form}
    )

def academic_fee_list(request):

    new_fees = AcademicFee.objects.filter(
        student_type='NEW'
    )

    old_fees = AcademicFee.objects.filter(
        student_type='OLD'
    )

    context = {
        'new_fees': new_fees,
        'old_fees': old_fees,
    }

    return render(
        request,
        'academic_fee_list.html',
        context
    )

def fee_receipt_create(request):

    if request.method == 'POST':
        form = FeeReceiptForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('fee_receipt_list')

    else:
        form = FeeReceiptForm()

    return render(
        request,
        'fee_receipt_create.html',
        {'form': form}
    )


def get_installment_amount(request):

    fee_id = request.GET.get('fee_id')
    installment = request.GET.get('installment')

    amount = 0

    try:
        fee = AcademicFee.objects.get(id=fee_id)

        if installment == 'FIRST':
            amount = fee.first_installment

        elif installment == 'SECOND':
            amount = fee.second_installment

        elif installment == 'THIRD':
            amount = fee.third_installment

    except AcademicFee.DoesNotExist:
        pass

    return JsonResponse({
        'amount': str(amount)
    })


def fee_receipt_list(request):
    receipts = FeeReceipt.objects.all().order_by('-id')

    return render(request, 'fee_receipt_list.html', {
        'receipts': receipts
    })


def fee_receipt_details(request, pk):
    receipt = FeeReceipt.objects.get(pk=pk)

    return render(request, 'fee_receipt_details.html', {
        'receipt': receipt
    })

def student_fee_due_list(request):

    dues = StudentFeeDue.objects.all()

    return render(
        request,
        'student_fee_due_list.html',
        {'dues': dues}
    )

