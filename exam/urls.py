from django.urls import path
from . import views

urlpatterns = [
    # Main Time Table View (Default pk=1)
    path('', views.timetable_detail_view, name='timetable_detail'),
    
    # Specific Time Table View by ID
    path('timetable/<int:pk>/', views.timetable_detail_view, name='timetable_detail_by_id'),
    path('new-exam/', views.new_exam, name='new_exam'),
    path('schedule-list/', views.exam_list_view, name='schedule_list'),
]