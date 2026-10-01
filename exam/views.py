from django.contrib import messages
from django.shortcuts import redirect, render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import ClassGroup, ExamDate, ExamSubject, TimeTable

# views.py

def timetable_detail_view(request, pk=1):
    timetable = get_object_or_404(TimeTable, pk=pk)
    class_groups = timetable.class_groups.all()
    exam_dates = timetable.dates.all()

    table_rows = []
    for ed in exam_dates:
        row_subjects = []
        for cg in class_groups:
            subject_obj = ed.subjects.filter(class_group=cg).first()
            
            if subject_obj and subject_obj.subject_name:
                # Comma (,) ko New Line (\n) me convert karein
                formatted_subject = subject_obj.subject_name.replace(',', '\n')
            else:
                formatted_subject = ""
                
            row_subjects.append(formatted_subject)
            
        table_rows.append({
            'date': ed.date,
            'day_name': ed.day_name,
            'subjects': row_subjects
        })

    context = {
        'timetable': timetable,
        'class_groups': class_groups,
        'table_rows': table_rows,
    }
    return render(request, 'timetable.html', context)

# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import TimeTable, ClassGroup, ExamDate, ExamSubject
from datetime import datetime

def new_exam(request):
    time_tables = TimeTable.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')

        # 1-CLICK SAVE: Create TimeTable, Class Groups, Dates, and Subjects together
        if action == 'one_click_save':
            school_name = request.POST.get('school_name', 'NAV CHETANA PUBLIC SCHOOL')
            title = request.POST.get('title')
            start_time = request.POST.get('start_time', '08:15')
            end_time = request.POST.get('end_time', '13:45')
            notice_text = request.POST.get('notice_text')

            # Step A: Create Master TimeTable
            tt = TimeTable.objects.create(
                school_name=school_name,
                title=title,
                start_time=start_time,
                end_time=end_time,
                notice_text=notice_text
            )

            # Step B: Get Class Group Names provided in Form
            class_names = request.POST.getlist('class_names[]')
            created_class_groups = []
            for order, name in enumerate(class_names, start=1):
                if name.strip():
                    cg = ClassGroup.objects.create(time_table=tt, name=name.strip(), order=order)
                    created_class_groups.append(cg)

            # Step C: Extract Dynamic Rows (Dates and Subjects)
            exam_dates = request.POST.getlist('exam_date[]')

            for row_idx, date_str in enumerate(exam_dates):
                if not date_str:
                    continue

                # Create Date Record
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                date_obj = ExamDate.objects.create(time_table=tt, date=parsed_date)

                # Link Subject for each created Class Group in this row
                for col_idx, cg in enumerate(created_class_groups):
                    field_name = f"subject_row_{row_idx}_col_{col_idx}"
                    subject_text = request.POST.get(field_name, '').strip()

                    if subject_text:
                        ExamSubject.objects.create(
                            exam_date=date_obj,
                            class_group=cg,
                            subject_name=subject_text
                        )

            messages.success(request, "🎉 TimeTable and Schedules Created in 1-Click!")
            return redirect('timetable_detail_by_id', pk=tt.id)

    return render(request, 'admin_add_exam.html', {'time_tables': time_tables})

def exam_list_view(request):
    time_tables = TimeTable.objects.all().prefetch_related('dates')
    today = timezone.now().date()

    exam_list = []
    for tt in time_tables:
        dates = tt.dates.all()
        
        if dates.exists():
            start_date = min(d.date for d in dates)
            end_date = max(d.date for d in dates)

            if today < start_date:
                status = 'Upcoming'
                status_color = 'bg-blue-100 text-blue-800 border-blue-300'
            elif start_date <= today <= end_date:
                status = 'Ongoing'
                status_color = 'bg-green-100 text-green-800 border-green-300'
            else:
                status = 'Past'
                status_color = 'bg-gray-100 text-gray-700 border-gray-300'
        else:
            start_date = None
            end_date = None
            status = 'No Schedule'
            status_color = 'bg-yellow-100 text-yellow-800 border-yellow-300'

        exam_list.append({
            'timetable': tt,
            'start_date': start_date,
            'end_date': end_date,
            'status': status,
            'status_color': status_color,
            'total_days': dates.count(),
        })

    context = {
        'exam_list': exam_list
    }
    return render(request, 'schedule_exam_list.html', context)