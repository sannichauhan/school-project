from rest_framework import viewsets
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import TeacherForm
from student.forms import AddressForm
from .models import Teacher, Designation, ClassTeacherAssignment, SubjectAssignment, Subject
from .serializers import (
    TeacherSerializer, DesignationSerializer, 
    ClassTeacherAssignmentSerializer, SubjectAssignmentSerializer
)

class DesignationViewSet(viewsets.ModelViewSet):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer

class TeacherViewSet(viewsets.ModelViewSet):
    # Optimized to fetch designation and address in a single query
    queryset = Teacher.objects.select_related('designation', 'address').all()
    serializer_class = TeacherSerializer

class ClassTeacherAssignmentViewSet(viewsets.ModelViewSet):
    queryset = ClassTeacherAssignment.objects.select_related('teacher', 'student_class').all()
    serializer_class = ClassTeacherAssignmentSerializer

class SubjectAssignmentViewSet(viewsets.ModelViewSet):
    queryset = SubjectAssignment.objects.select_related('teacher', 'subject', 'student_class').all()
    serializer_class = SubjectAssignmentSerializer


@login_required
def add_teacher_view(request):

    if request.method == "POST":

        teacher_form = TeacherForm(
            request.POST,
            request.FILES
        )

        address_form = AddressForm(request.POST)

        if teacher_form.is_valid() and address_form.is_valid():

            # save address first
            address = address_form.save()

            # save teacher
            teacher = teacher_form.save(commit=False)

            teacher.address = address

            teacher.save()

            messages.success(
                request,
                "Teacher added successfully"
            )

            return redirect("add_teacher")

    else:

        teacher_form = TeacherForm()

        address_form = AddressForm()

    context = {
        "teacher_form": teacher_form,
        "address_form": address_form,
        'page_title': 'Add New Teacher',
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Add New Teacher', 'url': ''},
        ]
    }

    return render(request, "add-teacher.html", context)

@login_required
def all_teacher_view(request):
     teacher = SubjectAssignment.objects.all()
     context = {
        'page_title': 'All Teachers',
        'teachers': teacher,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'All Teachers', 'url': ''},
        ]
    }
     return render(request, 'all-teacher.html', context)

def update_teacher_view(request, pk):

    teacher = get_object_or_404(Teacher, pk=pk)

    address = teacher.address

    if request.method == "POST":

        teacher_form = TeacherForm(
            request.POST,
            request.FILES,
            instance=teacher
        )

        address_form = AddressForm(
            request.POST,
            instance=address
        )

        if teacher_form.is_valid() and address_form.is_valid():

            address_form.save()

            teacher_form.save()

            messages.success(
                request,
                "Teacher updated successfully"
            )

            return redirect(
                "all_teacher"
            )

    else:

        teacher_form = TeacherForm(
            instance=teacher
        )

        address_form = AddressForm(
            instance=address
        )

    context = {
        "teacher_form": teacher_form,
        "address_form": address_form,
        "teacher": teacher,
        "page_title": "Update Teacher",
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'Update Teacher Data', 'url': ''},
        ]
    }

    return render(request, "add-teacher.html", context)

@login_required
def teacher_details_view(request, pk):
     teacher = Teacher.objects.get(pk=pk)
     context = {
        'page_title': 'All Teachers Data',
        'teachers':teacher,
        'breadcrumbs': [
            {'name': 'Home', 'url': '/'},
            {'name': 'All Teachers Data', 'url': ''},
        ]
    }
     return render(request, 'teacher-details.html', context)