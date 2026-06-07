from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from student.models import Student
from teacher.models import Teacher

from django.db.models import Sum

# Create your views here.

@login_required
def dashboard(request):

    total_students = Student.objects.count()

    male_students = Student.objects.filter(gender='Male').count()

    female_students = Student.objects.filter(gender='Female').count()

    total_teachers = Teacher.objects.count()

    teachers = Teacher.objects.all()


    context = {
        'total_students': total_students,
        'male_students': male_students,
        'female_students': female_students,
        'total_teachers': total_teachers,
        'teachers': teachers,
    }

    return render(request, 'index.html', context)