from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TeacherViewSet, DesignationViewSet, 
    ClassTeacherAssignmentViewSet, SubjectAssignmentViewSet, add_teacher_view, all_teacher_view, update_teacher_view,teacher_details_view
)

router = DefaultRouter()
router.register(r'profiles', TeacherViewSet)
router.register(r'designations', DesignationViewSet)
router.register(r'class-assignments', ClassTeacherAssignmentViewSet)
router.register(r'subject-assignments', SubjectAssignmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('add-teacher/', add_teacher_view, name='add-teacher'),
    path('all-teacher/', all_teacher_view, name='all-teacher'),
    path('update-teacher/<int:pk>/', update_teacher_view, name='update-teacher'),
    path('teacher-details/<int:pk>/', teacher_details_view, name='teacher-details'),
]