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
from exam.models import TimeTable
from .forms import AdmitCardForm, BulkAdmitCardForm


@login_required
def administration(request):
    return HttpResponse("Hello")  

@login_required
def admit_card_view(request):

    class_id = request.GET.get('class_id')

    admit_cards = AdmitCard.objects.select_related(
        'student',
        'student__current_class',
        'session',
        'exam_type'
    )

    if class_id:
        admit_cards = admit_cards.filter(
            student__current_class_id=class_id
        )

    admit_cards = admit_cards.order_by(
        'student__current_class__name',
        'student__name'
    )

    # --------------------------------
    # Class timetable
    # --------------------------------

    schedules = (
        ExamSchedule.objects
        .filter(student_class_id=class_id)
        .select_related('slot')
        .order_by(
            'slot__date',
            'slot__shift'
        )
    )

    # Date wise data
    timetable_data = defaultdict(dict)

    # Kaun-kaun se shifts available hain
    active_shifts = []

    shift_order = ['I', 'II', 'III']

    for schedule in schedules:

        date = schedule.slot.date
        shift = schedule.slot.shift

        timetable_data[date][shift] = schedule.subject

        if shift not in active_shifts:
            active_shifts.append(shift)

    # Shift ko I, II, III order me rakhen
    active_shifts = [
        shift for shift in shift_order
        if shift in active_shifts
    ]

    # Template ke liye list
    timetable_rows = []

    for date, shifts in timetable_data.items():

        row = {
            "date": date,
            "shifts": []
        }

        for shift in active_shifts:
            row["shifts"].append(
                shifts.get(shift, "")
            )

        timetable_rows.append(row)

    context = {
        'admit_cards': admit_cards,
        'timetable_rows': timetable_rows,
        'active_shifts': active_shifts,
    }

    return render(
        request,
        'admit-card.html',
        context
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




# =========================================================
# EXAM TIMETABLE DISPLAY
# =========================================================
@login_required
def exam_timetable_view(request):

    classes = StudentClass.objects.all().order_by('id')

    slots = (
        ExamSlot.objects
        .prefetch_related('schedules__student_class')
        .order_by('date', 'shift')
    )

    # -----------------------------------------
    # CLASS WISE DATA
    # -----------------------------------------

    class_wise_data = defaultdict(lambda: defaultdict(dict))

    for slot in slots:

        date = slot.date
        shift = slot.shift

        for schedule in slot.schedules.all():

            if schedule.student_class:

                class_id = schedule.student_class.id

                class_wise_data[class_id][date][shift] = (
                    schedule.subject
                )

    timetable = []

    shift_order = ['I', 'II', 'III']

    # -----------------------------------------
    # CLASS WISE TIMETABLE
    # -----------------------------------------

    for cls in classes:

        dates = []

        # -------------------------------------
        # FIND ACTIVE SHIFTS FOR THIS CLASS
        # -------------------------------------

        active_shifts = []

        for shift in shift_order:

            for date in class_wise_data[cls.id]:

                subject = class_wise_data[
                    cls.id
                ][date].get(shift, '')

                if subject:
                    active_shifts.append(shift)
                    break

        # -------------------------------------
        # CREATE DATE ROWS
        # -------------------------------------

        for date in sorted(
            class_wise_data[cls.id].keys()
        ):

            shifts = []

            for shift in active_shifts:

                shifts.append(
                    class_wise_data[
                        cls.id
                    ][date].get(shift, '')
                )

            dates.append({
                'date': date,
                'day': date.strftime('%A'),
                'shifts': shifts,
            })

        timetable.append({
            'class_id': cls.id,
            'class_name': str(cls),
            'dates': dates,
            'active_shifts': active_shifts,
        })

    return render(
        request,
        'exam-schedule.html',
        {
            'timetable': timetable,
            'classes': classes,
        }
    )


# =========================================================
# SAVE EXAM SCHEDULE
# =========================================================

def save_exam_schedule(request):

    if request.method == 'POST':

        date = request.POST.get('date')
        shift = request.POST.get('shift')
        student_class_id = request.POST.get('student_class')
        subject = request.POST.get('subject', '').strip()

        # -----------------------------------------
        # VALIDATION
        # -----------------------------------------

        if not date or not shift or not student_class_id:
            return redirect('exam_timetable')

        student_class = get_object_or_404(
            StudentClass,
            id=student_class_id
        )

        # -----------------------------------------
        # GET EXISTING SLOT OR CREATE NEW SLOT
        #
        # Same Date + Shift = SAME ExamSlot
        # -----------------------------------------

        slot, created = ExamSlot.objects.get_or_create(
            date=date,
            shift=shift
        )

        # -----------------------------------------
        # CREATE / UPDATE CLASS SCHEDULE
        #
        # Same slot + same class = one record
        # -----------------------------------------

        ExamSchedule.objects.update_or_create(
            slot=slot,
            student_class=student_class,
            defaults={
                'subject': subject
            }
        )

        return redirect('exam_timetable')

    return redirect('exam_timetable')
