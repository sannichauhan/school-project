from django.contrib.auth.decorators import login_required
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from collections import defaultdict
from .models import AdmitCard, TransferCertificate, Attendance, ExamSlot, ExamSchedule
from .forms import TransferCertificateForm, AdmitCardForm
from student.models import StudentClass, Student
from django.db import IntegrityError

@login_required
def administration(request):
    return HttpResponse("Hello")  
     
@login_required
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



@login_required
def create_tc_view(request):

    if request.method == 'POST':

        form = TransferCertificateForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('tc-list')

    else:

        form = TransferCertificateForm()
        context = {
            'page_title': 'Create Transfer Certificate',
            'form': form,
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Create Transfer Certificate', 'url': ''},
            ]
        }

    return render(request, 'create_tc.html', context)

@login_required
def tc_list_view(request):

    certificates = TransferCertificate.objects.select_related(
        'student'
    ).all()


    context = {
            'page_title': 'All Transfer Certificate',
            'certificates': certificates,
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'All Transfer Certificate', 'url': ''},
            ]
    }

    return render(request, 'tc_list.html', context)

@login_required
def tc_detail_view(request, pk):

    tc = get_object_or_404(
        TransferCertificate,
        pk=pk
    )

    return render(request, 'tc_detail.html', {'tc': tc})

@login_required
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
        'today': date.today(),
        'page_title': 'Mark Attendance',
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Mark Attendance', 'url': ''},
        ]
    }

    return render(
        request,
        'take_attendance.html',
        context
    )

@login_required
def attendance_report(request):

    records = Attendance.objects.select_related(
        'student',
        'student_class'
    )

    context = {
        'records': records,
        'page_title': 'Attendance Report',        
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Attendance Report', 'url': ''},
        ]
    }

    return render(request, 'attendance_report.html', context)


@login_required
def create_admit_card_view(request):
    if request.method == 'POST':
        form = AdmitCardForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Admit Card generated successfully!")
                # REDIRECT FIX: Send them back to your existing marksheet dashboard view
                return redirect('admit-card') 
            except IntegrityError:
                form.add_error(None, "An Admit Card already exists for this student in this academic session.")
    else:
        form = AdmitCardForm()

        context = {
            'page_title': 'Generate New Admit Card',
            'form': form,
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Generate New Admit Card', 'url': ''},
            ]
        }
        
    return render(request, 'create_admit_card.html', context)



@login_required
def exam_timetable_view(request):
    slots = ExamSlot.objects.prefetch_related('schedules').all()
    
    # Process and structure data to match the image grid
    matrix = defaultdict(lambda: {
        'NUR_UKG': {'I': 'Study', 'II': 'Study'},
        'I_VIII':  {'I': 'Study', 'II': 'Study'}
    })
    
    # Track days mapped to dates securely
    date_to_day = {}

    for slot in slots:
        date_str = slot.date.strftime('%d-%m-%Y')
        date_to_day[date_str] = slot.day
        
        for sched in slot.schedules.all():
            matrix[date_str][sched.class_category][slot.shift] = sched.subject

    # Flatten data structure for easy template looping
    timetable_data = []
    for date_str, categories in sorted(matrix.items(), key=lambda x: x[0]):
        timetable_data.append({
            'date': date_str,
            'day': date_to_day[date_str],
            'nursery_shift_1': categories['NUR_UKG'].get('I', 'Study'),
            'nursery_shift_2': categories['NUR_UKG'].get('II', 'Study'),
            'primary_shift_1': categories['I_VIII'].get('I', 'Study'),
            'primary_shift_2': categories['I_VIII'].get('II', 'Study'),
        })

    return render(request, 'exam-schedule.html', {'timetable': timetable_data})
