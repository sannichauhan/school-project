from django.urls import path, include
from rest_framework.routers import DefaultRouter

from teacher import views
from .views import (
    StudentClassViewSet, AddressViewSet, StudentViewSet, promote_students,
    SubjectViewSet, ExamViewSet, MarkSheetViewSet, MarksViewSet, add_class_view, student_list_view, student_registration_view,
    student_report_card_view, student_details_view, update_student_view, add_student_marks_view, all_students_marksheet_view, student_promotion_view, create_subject_view, subject_list_view, exam_list_view, exam_create_view, academic_session_list, academic_session_create, all_students_test_marksheet_view, test_report_card_view
)


router = DefaultRouter()
router.register(r'classes', StudentClassViewSet)
router.register(r'addresses', AddressViewSet)
router.register(r'students', StudentViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'exams', ExamViewSet)
router.register(r'marksheets', MarkSheetViewSet)
router.register(r'marks', MarksViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
    path('student-register/', student_registration_view, name='student-register'),
    path('students-list/', student_list_view, name='student-list'),
    path('student-details/<int:pk>/', student_details_view, name='student-details'),
    path('student-update/<int:pk>/', update_student_view, name='student-update'),        
    path('add-classes/', add_class_view, name='class-list'),    
    path('student-promotion/', student_promotion_view, name='student-promotion'),    
    path('add-student-marks/', add_student_marks_view, name="add-students-marks"),
    path('student-result/report-card/<int:pk>/', student_report_card_view, name='student-report-card'),
    path('all-student-marksheet/', all_students_marksheet_view, name="all-student-marksheet"),
    path('all-student-test-marksheet/', all_students_test_marksheet_view, name="all-student-test-marksheet"),
    path('student-result/test-report-card/<int:pk>/', test_report_card_view, name="test_report_card"),
    path('subjects-create/', create_subject_view, name='create_subject'),
    path('subjects-list/', subject_list_view, name='subject_list'),    
    path('exams-create/', exam_create_view, name='exam_create'),
    path('exams-list/', exam_list_view, name='exam_list'),
    path('academic-session/', academic_session_list, name='academic_session_list'),
    path('academic-session/add/', academic_session_create, name='academic_session_create'),
    path('promote/<int:class_id>/<int:session_id>/', promote_students, name='promote_student_base'),
]