from django.contrib import admin
from .models import Teacher, Designation, ClassTeacherAssignment, SubjectAssignment

class SubjectAssignmentInline(admin.TabularInline):
    model = SubjectAssignment
    extra = 1

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'designation', 'phone_number', 'is_active')
    list_filter = ('designation', 'is_active')
    search_fields = ('first_name', 'last_name', 'email')
    inlines = [SubjectAssignmentInline]

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    pass

@admin.register(ClassTeacherAssignment)
class ClassTeacherAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'student_class', 'academic_year')