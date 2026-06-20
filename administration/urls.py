from django.urls import path, include
from . import views
from .views import admit_card_view, create_tc_view, tc_list_view, tc_detail_view, take_attendance, attendance_report, create_admit_card_view


urlpatterns = [
    path('', views.administration),
    path("chaining/", include("smart_selects.urls")),
    path('admit-card/', admit_card_view, name='admit-card'),
    path('admit-card-generate/', create_admit_card_view, name='admit-card-generate'),
    path('transfer-certificate/create/', create_tc_view, name='tc-create'),
    path('transfer-certificate/list/', tc_list_view, name='tc-list'),
    path('transfer-certificate/<int:pk>/', tc_detail_view, name='tc-detail'),
    path('take-attendance/', take_attendance, name='take_attendance'),
    path('attendance-report/', attendance_report, name='attendance_report'),
    path('exam-schedule/', views.exam_timetable_view, name='exam_timetable'),
]