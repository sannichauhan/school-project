from rest_framework import viewsets
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Sum
from .models import StudentClass, Address, Student, Subject, Exam, MarkSheet, Marks, AcademicSession, TestMarkSheet, TestSubjectMark, AcademicSession
from .serializers import (
    StudentClassSerializer, AddressSerializer, StudentSerializer,
    SubjectSerializer, ExamSerializer, MarkSheetSerializer, MarksSerializer,
    StudentReportCardSerializer
)
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render, redirect
from django.db import transaction
from .forms import StudentAllInOneForm, AddressForm, StudentClassForm, SubjectForm, ExamForm, AcademicSessionForm
from django.contrib import messages
from django.db.models import Sum, F

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
                    
                    return redirect(request.path) # Change to your list view
            except Exception as e:
                # Handle database errors
                print(e)
                
                student_form.add_error(None, f"Database Error: {e}")
    else:
        student_form = StudentAllInOneForm()
        perm_addr_form = AddressForm(prefix='perm')
        local_addr_form = AddressForm(prefix='local')

    context = {
        'student_form': student_form,
        'perm_addr_form': perm_addr_form,
        'local_addr_form': local_addr_form,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Students', 'url': '/students/'},
            {'name': 'Add Student', 'url': ''},
        ]
    }
    return render(request, 'registration_form.html', context)


### Adding new class


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
    
    return render(request, 'add_class.html', {
        'form': form,
        'all_classes': all_classes
    })
    
    
### View students
def student_list_view(request):
    students = Student.objects.all()
    context = {
        'students': students,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Students', 'url': ''},
        ]
    }
    return render(request, 'student_list.html', context)

def student_details_view(request, pk):
    students = Student.objects.get(pk=pk)
    context = {
        'students': students,
    }
    return render(request, 'student-details.html', context)



def update_student_view(request, pk):

    student = get_object_or_404(Student, pk=pk)

    if request.method == "POST":
        form = StudentAllInOneForm(request.POST, request.FILES, instance=student)
        perm_addr_form = AddressForm(request.POST, prefix='perm', instance=student.permanent_address)
        local_addr_form = AddressForm(request.POST, prefix='local', instance=student.local_address)
        if (
            form.is_valid()
            and perm_addr_form.is_valid()
            and local_addr_form.is_valid()
        ):
            
            # Save address first
            permanent_address = perm_addr_form.save()
            local_address = local_addr_form.save()

            # Save student
            student_obj = form.save(commit=False)

            student_obj.permanent_address = permanent_address
            student_obj.local_address = local_address

            student_obj.save()

            messages.success(
                request,
                "Student updated successfully!"
            )

            return redirect(
                'student-update',
                pk=student.pk
            )
        else:
            print("error")
    else:
        form = StudentAllInOneForm(
            request.POST or None,
            request.FILES or None,
            instance=student
        )

        perm_addr_form = AddressForm(
            request.POST or None, prefix='perm',
            instance=student.permanent_address
        )

        local_addr_form = AddressForm(
            request.POST or None,
            prefix="local",
            instance=student.local_address
        )
        return render(
            request,
            "registration_form.html",
            {
                "student_form": form,
                "perm_addr_form": perm_addr_form,
                "local_addr_form": local_addr_form,
            }
        )

def add_student_marks_view(request):

    if request.method == "POST":

        student_class_id = request.POST.get("student_class")
        student_id = request.POST.get("student")
        exam_id = request.POST.get("exam")

        # Check duplicate marksheet
        if MarkSheet.objects.filter(
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
            student_class_id=student_class_id,
            student_id=student_id,
            exam_id=exam_id,
        )

        # Save subjects marks
        for i in range(9):
            
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

    return render(
        request,
        "student-marks.html",
        {
            "classes": classes,
            "exams": exams,
        },
    )


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
def student_report_card_view(request, pk):
    student = get_object_or_404(Student.objects.select_related('admission_class'), pk=pk)
    
    # 1. Get all subjects for this class
    subjects = Subject.objects.filter(student_class=student.admission_class)
    
    # 2. Get all distinct exams that have marks for this student
    exams = Exam.objects.filter(marksheet__student=student).distinct().order_by('id')
    
    # 3. Fetch all marks and pre-calculate row totals
    marks_list = Marks.objects.filter(
        marksheet__student=student
    ).select_related('subject', 'marksheet__exam')

    report_matrix = {}
    subject_totals = {}
    # marksheet = MarkSheet.objects.filter(student=student)
    
    for sub in subjects:
        report_matrix[sub.id] = {}
        row_total = 0
        for exam in exams:
            mark = marks_list.filter(subject=sub, marksheet__exam=exam).first()
            report_matrix[sub.id][exam.id] = mark
            if mark:
                row_total += (mark.test_marks or 0) + (mark.written_marks or 0)
        subject_totals[sub.id] = row_total

    # 5. Calculate the Final Grand Total (Bottom Right Cell)
    # Final Grand Total
    total_score = sum(subject_totals.values())

    # Total Maximum Marks
    max_marks = sum(
        mark.max_total for mark in marks_list
    )

    # Percentage
    percentage = round(
        (total_score / max_marks) * 100,
        2
    ) if max_marks > 0 else 0


    # Total exam columns
    if exams.count() == 1:
        total_exam_columns = 4

    elif exams.count() == 2:
        total_exam_columns = 6

    elif exams.count() == 3:
        total_exam_columns = 8

    else:
        total_exam_columns = exams.count() * 2

    

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




def all_students_marksheet_view(request):
    students = Student.objects.all()    
    return render(request, 'all-student-marksheet.html', {'students': students})



def student_promotion_view(request):

    sessions = AcademicSession.objects.all()
    classes = StudentClass.objects.all()

    if request.method == "POST":
        current_session = request.POST.get("current_session")
        promote_session = request.POST.get("promote_session")
        promotion_from_class = request.POST.get("promotion_from_class")
        promotion_to_class = request.POST.get("promotion_to_class")

        current_session_obj = AcademicSession.objects.get(id=current_session)
        promote_session_obj = AcademicSession.objects.get(id=promote_session)

        from_class = StudentClass.objects.get(id=promotion_from_class)
        to_class = StudentClass.objects.get(id=promotion_to_class)

        StudentPromotion.objects.create(
            current_session=current_session_obj,
            promote_session=promote_session_obj,
            promotion_from_class=from_class,
            promotion_to_class=to_class
        )

        students = Student.objects.filter(
            admission_class=from_class,
            session=current_session_obj
        )

        total = students.count()

        for student in students:
            student.admission_class = to_class
            student.session = promote_session_obj
            student.roll_number = 0
            student.save()

        messages.success(
            request,
            f"{total} students promoted successfully."
        )

        return redirect("student-promotion")

    context = {
        "sessions": sessions,
        "classes": classes,
    }

    return render(
        request,
        "student-promotion.html",
        context
    )

def create_subject_view(request):
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subject_list')  # list page pe bhej dega
    else:
        form = SubjectForm()

    return render(request, 'subject_form.html', {'form': form})

def subject_list_view(request):
    subjects = Subject.objects.select_related('student_class').all()
    return render(request, 'subject_list.html', {'subjects': subjects})

# CREATE
def exam_create_view(request):
    form = ExamForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('exam_list')
    return render(request, 'exam_form.html', {'form': form})


# LIST
def exam_list_view(request):
    exams = Exam.objects.all().order_by('-id')
    return render(request, 'exam_list.html', {'exams': exams})

def academic_session_create(request):
    if request.method == "POST":
        form = AcademicSessionForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('academic_session_list')
    else:
        form = AcademicSessionForm()

    return render(request, 'session-create.html', {
        'form': form
    })


def academic_session_list(request):
    sessions = AcademicSession.objects.all().order_by('-start_date')

    return render(request, 'session-list.html', {
        'sessions': sessions
    })

# Test Marksheet

def get_subjects_view(request):

    class_id = request.GET.get('student_class')

    subjects = Subject.objects.filter(
        student_class_id=class_id
    )

    data = []

    for subject in subjects:
        data.append({
            "id": subject.id,
            "name": subject.name,
        })

    return JsonResponse(data, safe=False)

def test_marks_entry_view(request):

    classes = StudentClass.objects.all()
    exams = Exam.objects.all()

    if request.method == "POST":

        class_id = request.POST.get("student_class")
        student_id = request.POST.get("student")
        exam_id = request.POST.get("exam")

        if not class_id or not student_id or not exam_id:

            messages.error(
                request,
                "Please select Class, Student and Exam."
            )

            return redirect("test_marks_entry")

        marksheet, created = TestMarkSheet.objects.get_or_create(
            student_class_id=class_id,
            student_id=student_id,
            exam_name_id=exam_id
        )

        if not created:
            messages.error(
                request,
                "Marks already entered for this student."
            )
            return redirect("test_marks_entry")

        total_forms = int(
            request.POST.get(
                "form-TOTAL_FORMS",
                0
            )
        )

        for i in range(total_forms):

            subject_id = request.POST.get(
                f"form-{i}-subject"
            )

            obtained_marks = request.POST.get(
                f"form-{i}-obtained_marks"
            ) or 0

            remarks = request.POST.get(
                f"form-{i}-remarks"
            ) or ""

            max_marks = request.POST.get(
                f"form-{i}-max_marks"
            ) or 15

            if subject_id:

                TestSubjectMark.objects.create(
                    marksheet=marksheet,
                    subject_id=subject_id,
                    obtained_marks=obtained_marks,
                    max_marks=max_marks,
                    remarks=remarks
                )

        messages.success(
            request,
            "Marks Saved Successfully."
        )

        return redirect("test_marks_entry")

    return render(
        request,
        "test_marks_entry.html",
        {
            "classes": classes,
            "exams": exams,
        }
    )

def student_test_report_card_view(request, pk):
    marksheet = get_object_or_404(TestMarkSheet.objects.select_related('student', 'student__admission_class'), pk=pk)
    student = marksheet.student
    marksheet = get_object_or_404(TestMarkSheet, pk=pk)
    marks = TestSubjectMark.objects.filter(marksheet=marksheet)
    exams = Exam.objects.filter(testmarksheet__student=student).distinct().order_by('id')

    # Calculate totals dynamically
    total_max = marks.aggregate(Sum('max_marks'))['max_marks__sum'] or 0
    total_obtained = marks.aggregate(Sum('obtained_marks'))['obtained_marks__sum'] or 0
    
    # Calculate percentage safely
    percentage = (total_obtained / total_max * 100) if total_max > 0 else 0

    # 1. Determine Status (Pass/Fail) - e.g., passing mark is 33%
    if percentage >= 33:
        status = "PASS"
    else:
        status = "FAIL"

    # 2. Determine Grade based on standard school metrics
    if percentage >= 91:
        grade = "A1"
    elif percentage >= 81:
        grade = "A2"
    elif percentage >= 71:
        grade = "B1"
    elif percentage >= 61:
        grade = "B2"
    elif percentage >= 51:
        grade = "C1"
    elif percentage >= 41:
        grade = "C2"
    elif percentage >= 33:
        grade = "D"
    else:
        grade = "E (Essential Repeat)"

    context = {
        "marksheet": marksheet,
        "marks": marks,
        "total_max": total_max,
        'exams': exams,
        'student': student,
        "total_obtained": total_obtained,
        "percentage": round(percentage, 2),
        "status": status,
        "grade": grade,
    }

    return render(request, "test_report_card.html", context)

# def all_student_test_marksheet(request):
#     students = Student.objects.all()    
#     return render(request, 'all-student-test-marksheet.html', {'students': students})

def all_student_test_marksheet(request):
    marksheets = TestMarkSheet.objects.select_related('student', 'student__admission_class', 'exam_name').all()
    # The key here MUST match the template loop variable
    return render(request, 'all-student-test-marksheet.html', {'marksheets': marksheets})