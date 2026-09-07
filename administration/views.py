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
from .models import Student, AdmitCard
from exam.models import TimeTable, ClassGroup
from .forms import AdmitCardForm, BulkAdmitCardForm

@login_required
def administration(request):
    return HttpResponse("Hello")  

@login_required
def admit_card_view(request):
  class_id = request.GET.get('class_id')

  admit_cards = AdmitCard.objects.select_related(
      'student', 'student__admission_class', 'session', 'exam_type'
  )

  if class_id:
    admit_cards = admit_cards.filter(student__admission_class_id=class_id)

  admit_cards = admit_cards.order_by(
      'student__admission_class__name', 'student__name'
  )

  # --- Timetable & Class Groups Context Data ---
  # TimeTable fetch karein (Latest active timetable)
  timetable = TimeTable.objects.last()

  table_rows = []
  class_groups = []

  if timetable:
    class_groups = timetable.class_groups.all().order_by('order')
    exam_dates = timetable.dates.all().order_by('date')

    for ed in exam_dates:
      row_subjects = []
      for cg in class_groups:
        subject_obj = ed.subjects.filter(class_group=cg).first()
        if subject_obj and subject_obj.subject_name:
          formatted_subject = subject_obj.subject_name.replace(',', '\n')
        else:
          formatted_subject = ''
        row_subjects.append(formatted_subject)

      table_rows.append({
          'date': ed.date,
          'day_name': ed.day_name,
          'subjects': row_subjects,
      })

  # Complete Context Dictionary
  context = {
      'admit_cards': admit_cards,
      'timetable': timetable,
      'class_groups': class_groups,
      'table_rows': table_rows,
  }

  return render(request, 'admit-card.html', context)



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
            current_class=selected_class
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
            'form': form,
            'page_title': 'Generate New Admit Card', 
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


@login_required
def id_cards_view(request):
    students = Student.objects.all()
    context = {
        'students' : students
    }
    return render(request, 'id-card.html', context)


def bulk_generate_admit_card(request):

    if request.method == 'POST':

        form = BulkAdmitCardForm(request.POST)

        if form.is_valid():

            session = form.cleaned_data['session']
            exam_type = form.cleaned_data['exam_type']
            student_class = form.cleaned_data['student_class']
            exam_start_date = form.cleaned_data['exam_start_date']
            exam_end_date = form.cleaned_data['exam_end_date']
            remarks = form.cleaned_data['remarks']

            # Class ke students
            students = Student.objects.filter(
                admission_class=student_class
            )

            created_count = 0
            skipped_count = 0

            for student in students:

                # Check duplicate
                already_exists = AdmitCard.objects.filter(
                    student=student,
                    session=session,
                    exam_type=exam_type
                ).exists()

                if already_exists:
                    skipped_count += 1
                    continue

                try:

                    AdmitCard.objects.create(
                        student=student,
                        session=session,
                        exam_type=exam_type,
                        exam_start_date=exam_start_date,
                        exam_end_date=exam_end_date,
                        remarks=remarks
                    )

                    created_count += 1

                except IntegrityError:
                    skipped_count += 1

            messages.success(
                request,
                f"{created_count} Admit Cards generated successfully."
            )

            if skipped_count > 0:
                messages.warning(
                    request,
                    f"{skipped_count} Admit Cards already existed and were skipped."
                )

            return redirect('admit-card')

    else:
        form = BulkAdmitCardForm()

    context = {
        'form': form,
        'page_title': 'Bulk Generate Admit Cards',
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Bulk Generate Admit Cards', 'url': ''},
        ]
    }

    return render(
        request,
        'bulk_generate_admit_card.html',
        context
    )

