from multiprocessing import context

from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from django.contrib import messages

from django.db import transaction
from .serializers import (
    StudentClassSerializer, AddressSerializer, StudentSerializer,
    SubjectSerializer, ExamSerializer, MarkSheetSerializer, MarksSerializer,
    StudentReportCardSerializer
)
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render, redirect
from .models import StudentClass, Address, Student, Subject, Exam, MarkSheet, Marks, AcademicSession, AcademicSession
from .forms import StudentAllInOneForm, AddressForm, StudentClassForm, SubjectForm, ExamForm, AcademicSessionForm, StudentPromotionForm


class StudentClassViewSet(viewsets.ModelViewSet):
    queryset = StudentClass.objects.all()
    serializer_class = StudentClassSerializer

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

class StudentViewSet(viewsets.ModelViewSet):
    # Optimized to load addresses and class in one database query
    queryset = Student.objects.select_related('admission_class', 'permanent_address', 'local_address').all()
    serializer_class = StudentSerializer
    
    @action(detail=True, methods=['get'], url_path='report-card')
    def get_report_card(self, request, pk=None):
        student = self.get_object()
        
        # 1. Fetch all marks for this student across all exams
        all_marks = Marks.objects.filter(marksheet__student=student).select_related('subject', 'marksheet__exam')
        
        # 2. Group data by subject
        subject_map = {}
        for mark in all_marks:
            sub_name = mark.subject.name
            exam_name = mark.marksheet.exam.name
            
            if sub_name not in subject_map:
                subject_map[sub_name] = {"subject": sub_name, "marks": {}}
            
            subject_map[sub_name]["marks"][exam_name] = {
                "test": mark.test_marks,
                "written": mark.written_marks
            }
            
        
        # 3. Construct the final object
        report_data = {
            "student_name": student.name,
            "admission_class": student.admission_class.name,
            "subjects": list(subject_map.values())
        }
        
        serializer = StudentReportCardSerializer(report_data)
        return Response(serializer.data)

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.select_related('student_class').all()
    serializer_class = SubjectSerializer

    def get_queryset(self):

        queryset = Subject.objects.select_related(
            'student_class'
        ).all()

        student_class = self.request.query_params.get(
            'student_class'
        )

        if student_class:
            queryset = queryset.filter(
                student_class_id=student_class
            )

        return queryset
    

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer

class MarkSheetViewSet(viewsets.ModelViewSet):
    # Prefetch subject_marks to avoid N+1 query issues
    queryset = MarkSheet.objects.select_related('student', 'exam', 'student_class').prefetch_related('subject_marks').all()
    serializer_class = MarkSheetSerializer

class MarksViewSet(viewsets.ModelViewSet):
    queryset = Marks.objects.select_related('marksheet', 'subject').all()
    serializer_class = MarksSerializer
    


 
@login_required
def student_registration_view(request):
    if request.method == 'POST':
        # Create instances using POST data
        student_form = StudentAllInOneForm(request.POST, request.FILES)
        perm_addr_form = AddressForm(request.POST, prefix='perm')
        local_addr_form = AddressForm(request.POST, prefix='local')

        if student_form.is_valid() and perm_addr_form.is_valid() and local_addr_form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Save Permanent Address
                    perm_address = perm_addr_form.save()
                    
                    # 2. Save Local Address
                    local_address = local_addr_form.save()

                    # 3. Save Student and link the addresses
                    student = student_form.save(commit=False)
                    student.permanent_address = perm_address
                    student.local_address = local_address
                    student.save()

                    messages.success(
                        request,
                        f"Student '{student.name}' registered successfully."
                    )

                    
                    
                    return redirect(request.path) # Change to your list view
            except Exception as e:
                # Handle database errors
                print(e)
                
                student_form.add_error(None, f"Database Error: {e}")
        else:
            messages.error(
                request,
                "Please correct the errors below and try again."
            )

    else:
        student_form = StudentAllInOneForm()
        perm_addr_form = AddressForm(prefix='perm')
        local_addr_form = AddressForm(prefix='local')

    context = {
        'student_form': student_form,
        'perm_addr_form': perm_addr_form,
        'local_addr_form': local_addr_form,
        'page_title': 'Add New Students',
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Students', 'url': '/students/'},
            {'name': 'Add New Students', 'url': ''},
        ]
    }
    return render(request, 'registration_form.html', context)


### Adding new class

@login_required
def add_class_view(request):
    if request.method == 'POST':
        form = StudentClassForm(request.POST)        
        if form.is_valid():
            form.save()
            return redirect("class-list") # Redirect to a list of all classes
    
    else:
        form = StudentClassForm()
    
    # Fetch all classes to show them on the same page
    all_classes = StudentClass.objects.all().order_by('name')

    context = {
        'form': form,
        'all_classes': all_classes,
        'page_title': 'Add New Class',
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Add New Class', 'url': ''},
        ]
    }
    
    return render(request, 'add_class.html', context)
    
    
### View students
@login_required
def student_list_view(request):
    students = Student.objects.all()
    context = {
        'page_title': 'All Students',
        'students': students,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Students', 'url': ''},
        ]
    }
    return render(request, 'student_list.html', context)

@login_required
def student_details_view(request, pk):
    students = Student.objects.get(pk=pk)
    context = {
        'students': students,
        'page_title': 'Details of Students',        
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Details of Students', 'url': ''},
        ]
    }
    return render(request, 'student-details.html', context)


@login_required
def update_student_view(request, pk):
    student = get_object_or_404(Student, pk=pk)

    if request.method == "POST":
        form = StudentAllInOneForm(
            request.POST,
            request.FILES,
            instance=student
        )

        perm_addr_form = AddressForm(
            request.POST,
            prefix='perm',
            instance=student.permanent_address
        )

        local_addr_form = AddressForm(
            request.POST,
            prefix='local',
            instance=student.local_address
        )

        if (
            form.is_valid()
            and perm_addr_form.is_valid()
            and local_addr_form.is_valid()
        ):

            permanent_address = perm_addr_form.save()
            local_address = local_addr_form.save()

            student_obj = form.save(commit=False)
            student_obj.permanent_address = permanent_address
            student_obj.local_address = local_address
            student_obj.save()

            messages.success(
                request,
                "Student updated successfully!"
            )

            return redirect('student-list')

        else:
            print("Student Errors:", form.errors)
            print("Perm Errors:", perm_addr_form.errors)
            print("Local Errors:", local_addr_form.errors)

    else:
        form = StudentAllInOneForm(instance=student)

        perm_addr_form = AddressForm(
            prefix='perm',
            instance=student.permanent_address
        )

        local_addr_form = AddressForm(
            prefix='local',
            instance=student.local_address
        )

        context = {
            "student_form": form,
            "perm_addr_form": perm_addr_form,
            "local_addr_form": local_addr_form,            
            'page_title': 'Update Student Details',
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Update Student Details', 'url': ''},
            ]
        }

    return render(request, "registration_form.html", context)
@login_required
def add_student_marks_view(request):

    if request.method == "POST":

        academic_session_id = request.POST.get("academic_session")
        student_class_id = request.POST.get("student_class")
        student_id = request.POST.get("student")
        exam_id = request.POST.get("exam")


        # Check duplicate marksheet
        if MarkSheet.objects.filter(
            academic_session_id=academic_session_id,
            student_id=student_id,
            exam_id=exam_id
        ).exists():

            messages.error(
                request,
                "Marks already added for this student and exam."
            )

            return redirect("add-students-marks")

        # Create parent marksheet
        marksheet = MarkSheet.objects.create(
            academic_session_id=academic_session_id,
            student_class_id=student_class_id,
            student_id=student_id,
            exam_id=exam_id,
        )

        # Save subjects marks
        for i in range(20):
            
            subject_id = request.POST.get(f"form-{i}-subject")

            if not subject_id:
                continue

            Marks.objects.create(

                marksheet=marksheet,

                subject_id=subject_id,

                test_marks=request.POST.get(
                    f"form-{i}-test_marks", 0
                ),

                written_marks=request.POST.get(
                    f"form-{i}-written_marks", 0
                ),

                max_test_marks=request.POST.get(
                    f"form-{i}-max_test_marks", 0
                ),

                max_written_marks=request.POST.get(
                    f"form-{i}-max_written_marks", 0
                ),
            )

        messages.success(request, "Marks added successfully.")

        return redirect("add-students-marks")

    classes = StudentClass.objects.prefetch_related(
        "students"
    ).all()

    exams = Exam.objects.all()
    sessions = AcademicSession.objects.all()

    context = {
        "classes": classes,
        "exams": exams,
        "sessions": sessions,
        'page_title': 'Add Student Marks',
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Add Student Marks', 'url': ''},
        ]
    }

    return render(request, "student-marks.html", context)



def grade(percentage):
    
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    elif percentage >= 50:
        return "D"
    elif percentage >= 33:
        return "E"

    return "F"

### Report card view for students
@login_required
def student_report_card_view(request, pk):
    student = get_object_or_404(Student.objects.select_related('admission_class'), pk=pk)
    
    # 1. Get all subjects for this class
    subjects = Subject.objects.filter(student_class=student.admission_class)
    
    # 2. Get all distinct exams
    exams = Exam.objects.filter(marksheet__student=student).distinct().order_by('id')
    
    # 3. Fetch all marks in a single query
    marks_list = Marks.objects.filter(
        marksheet__student=student
    ).select_related('subject', 'marksheet__exam')

    # Optimization: Convert QuerySet into a Python Dictionary for instant lookup
    # Key format: (subject_id, exam_id) -> mark_object
    marks_dict = {
        (m.subject_id, m.marksheet.exam_id): m for m in marks_list
    }

    report_matrix = {}
    subject_totals = {}

    
    
    for sub in subjects:
        report_matrix[sub.id] = {}
        row_total = 0
        for exam in exams:
            # Memory se fast lookup bina database ko hit kiye
            mark = marks_dict.get((sub.id, exam.id))
            report_matrix[sub.id][exam.id] = mark
            
            if mark:
                row_total += (mark.test_marks or 0) + (mark.written_marks or 0)
        
        subject_totals[sub.id] = row_total

    # Final Grand Total Calculation
    total_score = sum(subject_totals.values())
    
    max_marks = 0

    for mark in marks_list:
        exam_name = mark.marksheet.exam.name.lower()
        
        # Dono type ki spellings check kar rahe hain (safe side)
        if 'quaterly' in exam_name or 'quarterly' in exam_name:
            max_marks += (mark.max_test_marks or 0)
        else:
            max_marks += (
                (mark.max_test_marks or 0) +
                (mark.max_written_marks or 0)
            )

    # Percentage
    percentage = round((total_score / max_marks) * 100, 2) if max_marks > 0 else 0

    # Total exam columns
    total_exam_columns = exams.count() * 2 if exams.count() > 3 else {1:4, 2:6, 3:8}.get(exams.count(), 0)

    return render(request, 'report_card.html', {
        'student': student,
        'subjects': subjects,
        'exams': exams,
        'report_matrix': report_matrix,
        'subject_totals': subject_totals,
        'total_score': total_score,
        'percentage' : percentage,
        'max_marks' : max_marks,
        'total_exam_columns' : total_exam_columns,
        'grade' : grade(percentage),
    })

@login_required
def all_students_marksheet_view(request):
    students = Student.objects.all()
    context = {
        'page_title': 'All Student Result List',
        'students': students,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'All Student Result List', 'url': ''},
        ]
    }    
    return render(request, 'all-student-marksheet.html', context)


@login_required
def student_promotion_view(request):
    # 1. 'UnboundLocalError' से बचने के लिए वेरिएबल्स को शुरुआत में ही डिफ़ॉल्ट None वैल्यू दें
    current_session_id = None
    from_class_id = None

    # 2. POST और GET दोनों से रॉ डेटा सुरक्षित रूप से निकालें
    raw_session = request.POST.get('current_session') or request.GET.get('current_session')
    raw_class = request.POST.get('promotion_from_class') or request.GET.get('promotion_from_class')

    # 3. सुरक्षित रूप से इंटीजर (Integer) में कन्वर्ट करें
    try:
        if raw_session:
            current_session_id = int(raw_session)
        if raw_class:
            from_class_id = int(raw_class)
    except (ValueError, TypeError):
        # यदि कन्वर्शन फेल होता है, तो वैल्यू पहले से ही None सेट है
        pass

    if request.method == 'POST':
        form = StudentPromotionForm(
            request.POST, 
            current_session_id=current_session_id, 
            from_class_id=from_class_id
        )
        
        # यदि यूज़र ने सिर्फ 'Load Students List' बटन दबाया है
        if 'fetch_students' in request.POST:
            form = StudentPromotionForm(
                current_session_id=current_session_id, 
                from_class_id=from_class_id, 
                initial=request.POST
            )
        
        # यदि यूज़र ने 'Execute Promotion Flow' सबमिट किया है और फॉर्म वैलिड है
        elif form.is_valid():
            prom_session = form.cleaned_data['promote_session']
            to_cls = form.cleaned_data['promotion_to_class']
            selected_histories = form.cleaned_data['students']

            if not selected_histories:
                messages.error(request, "Please select at least one student to promote.")
            else:
                try:
                    # सिलेक्टेड स्टूडेंट हिस्ट्री रिकॉर्ड्स से छात्र की IDs निकालें
                    student_ids = [history.student_id for history in selected_histories]
                    
                    # यूजर का नाम ट्रैक करें
                    user_name = str(request.user if request.user.is_authenticated else "Admin")
                    
                    # महा-ऑप्टिमाइज्ड फ़ंक्शन को कॉल करें
                    promoted_count = promote_students(
                        student_ids=student_ids,
                        target_class_id=to_cls.id,
                        target_session_id=prom_session.id,
                        user_name=user_name
                    )

                    if promoted_count > 0:
                        messages.success(request, f"Successfully promoted {promoted_count} students.")
                    else:
                        messages.warning(request, "No new students were promoted (they might have been promoted already).")
                        
                    return redirect('promote_students')  # अपनी सही URL नाम/नेमस्पेस यहाँ डालें
                    
                except Exception as e:
                    messages.error(request, f"An error occurred during promotion: {str(e)}")
    else:
        form = StudentPromotionForm(current_session_id=current_session_id, from_class_id=from_class_id)

    # 4. टेम्पलेट में टेबल या ड्रॉपडाउन दिखाने के लिए वेरिफिकेशन लॉजिक
    # has_students = False
    # if current_session_id and from_class_id:
    #     has_students = StudentAcademicHistory.objects.filter(
    #         session_id=current_session_id,
    #         student_class_id=from_class_id,
    #         is_active=True
    #     ).exists()

    context = {
        'sessions': AcademicSession.objects.all(),
        'classes': StudentClass.objects.all(),
        'form': form,
        # 'has_students': has_students,
        'current_session_id': current_session_id,
        'from_class_id': from_class_id,
        'page_title': 'Student Promotion',
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Student Promotion', 'url': ''},
        ]
    }

    return render(request, "student-promotion.html", context)
@login_required
def create_subject_view(request):
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subject_list')  # list page pe bhej dega
    else:
        form = SubjectForm()

        context = {
            'page_title': 'Add New Subject',
            'form': form,
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Add New Subject', 'url': ''},
            ]
        }

    return render(request, 'subject_form.html', context)


@login_required
def subject_list_view(request):
    subjects = Subject.objects.select_related('student_class').all()
    context = {
            'subjects': subjects,
            'page_title': 'Subject List',            
            'breadcrumbs': [
                {'name': 'Home', 'url': '/'},
                {'name': 'Subject List', 'url': ''},
            ]
    }
    
    return render(request, 'subject_list.html', context)

# CREATE
@login_required
def exam_create_view(request):
    form = ExamForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('exam_list')
    context = {
        'form': form,
        'page_title': 'Add New Exam & Academic Session',            
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Add New Exam & Academic Session', 'url': ''},
        ]
    }
    return render(request, 'exam_form.html', context)


# LIST
@login_required
def exam_list_view(request):
    exams = Exam.objects.all().order_by('-id')
    context = {
        'exams': exams,
        'page_title': 'Exam List & Academic Session',
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Exam List & Academic Session', 'url': ''},
        ]
    }
    return render(request, 'exam_list.html', context)

@login_required
def academic_session_create(request):
    if request.method == "POST":
        form = AcademicSessionForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('academic_session_list')
    else:
        form = AcademicSessionForm()

    context = {
        'form': form,
        'page_title': 'Add Academic Session',
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Add Academic Session', 'url': ''},
        ]
    }
    return render(request, 'session-create.html', context)


@login_required
def academic_session_list(request):
    sessions = AcademicSession.objects.all().order_by('-start_date')
    context = {
        'sessions': sessions,
        'page_title': 'Academic Sessions',
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Academic Sessions', 'url': ''},
        ]
    }
    return render(request, 'session-list.html', context)

@login_required
def all_students_test_marksheet_view(request):
    marksheets = MarkSheet.objects.select_related('student', 'student_class', 'exam').all()    
    context = {
        'page_title': 'All Student Test Result List',
        'marksheets': marksheets,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'All Student Test Result List', 'url': ''},
        ]
    }   
    return render(request, 'all-student-test-marksheet.html', context)



@login_required
def test_report_card_view(request, pk):
    # सभी marksheets को fetch करना
    marksheet = get_object_or_404(
        MarkSheet.objects.select_related('student', 'student_class', 'exam').prefetch_related('subject_marks'), 
        pk=pk
    )
    marks = marksheet.subject_marks.filter(max_test_marks__gt=0)
    total_obtained = sum(mark.test_marks or 0 for mark in marks)
    total_max = sum(mark.max_test_marks or 0 for mark in marks)
    percentage = round((total_obtained / total_max) * 100, 2) if total_max else 0

    # Grade
    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B+"
    elif percentage >= 60:
        grade = "B"
    elif percentage >= 50:
        grade = "C"
    elif percentage >= 33:
        grade = "D"
    else:
        grade = "F"

    # Result Status
    result_status = "Pass" if percentage >= 33 else "Fail"
    context = {
        'marksheet': marksheet,
        'marks': marks,
        'total_obtained': total_obtained,
        'total_max': total_max,
        'percentage': percentage,
        'grade': grade,
        'result_status': result_status,
    }   
    return render(request, 'test_report_card.html', context)

@login_required
def promote_students(request, class_id=None, session_id=None):

    from .servicesOLd import bulk_promote_students_with_ledger
    if request.method == 'POST':
        student_ids = request.POST.getlist('student_ids')
        from_class_id = request.POST.get('from_class_id')
        target_session_id = request.POST.get('target_session_id')
        
        target_class = get_object_or_404(StudentClass, id=from_class_id)
        target_session = get_object_or_404(AcademicSession, id=target_session_id)

        promoted_count = 0

        try:
            with transaction.atomic():
                created = bulk_promote_students_with_ledger(
                    academic_year_id=target_session.id,
                    student_ids=student_ids,
                    from_class_id=target_class.id
                )
                
                if created > 0:
                    promoted_count += len(student_ids)
                    messages.success(request,f"Students are promoted successfully.")
                    return redirect(request.path)
                else:
                    messages.warning(request, f"No new students were promoted (they might have been promoted already).")
                    return redirect(request.path)
        except Exception as e:
            messages.error(request, f"An error occurred during promotion: {str(e)}")
            return redirect(request.path)
    else:
        context = {
        'page_title': 'Bulk Student Promotion',
        'all_classes': StudentClass.objects.all(),
        'all_sessions': AcademicSession.objects.all(),
        'students': Student.objects.filter(current_class_id=class_id) if class_id and session_id else [],
        'selected_class': StudentClass.objects.filter(id=class_id).first() if class_id else StudentClass.objects.first(),
        'selected_session': AcademicSession.objects.filter(id=session_id).first() if session_id else AcademicSession.objects.first(),
    }
    return render(request, 'promote_student.html', context)
        