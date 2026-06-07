from django.contrib import admin
from .models import StudentClass, Address, Student, Subject, Exam, MarkSheet, Marks, AcademicSession

# --- Inlines for a better UI ---

class AddressInline(admin.StackedInline):
    model = Address
    extra = 0 # Prevents empty extra forms from showing up automatically

class MarksInline(admin.TabularInline):
    model = Marks
    extra = 1
    fields = [
        'subject',
        'test_marks',
        'max_test_marks',
        'written_marks',
        'max_written_marks',
        'obtained_total',
        'max_total',
    ]

    readonly_fields = [
        'obtained_total',
        'max_total',
    ]

    def total_display(self, obj):
        return obj.total_marks
    total_display.short_description = "Total"

# --- Main Admin Classes ---

@admin.register(StudentClass)
class StudentClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'section')
    search_fields = ('name',)

@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ('start_year', 'end_year')
    search_fields = ('start_year', 'end_year')
    ordering = ('-start_year',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name','roll_number', 'admission_class', 'contact_number', 'gender', 'created_at')
    list_filter = ('admission_class', 'gender', 'religion')
    search_fields = ('name', 'adhaar_number', 'contact_number')
    
    # Organize fields into sections (Fieldsets)
    fieldsets = (
        ('Personal Info', {
            'fields': ('name', 'student_photo', 'date_of_birth', 'gender', 'religion', 'category', 'adhaar_number', 'pen_number')
        }),
        ('Academic & Contact', {
            'fields': ('admission_class', 'contact_number', 'father_name', 'mother_name', 'last_institution', 'session', 'choose_school', 'conveyance_facility')
        }),
        ('Addresses', {
            'fields': ('permanent_address', 'local_address')
        }),
    )

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_class', 'max_test_marks', 'max_written_marks')
    list_filter = ('student_class',)

@admin.register(MarkSheet)
class MarkSheetAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'student_class')
    list_filter = ('exam', 'student_class')
    inlines = [MarksInline] # Allows entering marks directly inside the marksheet

    

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_year')

# We register Address separately just in case you need to edit an address independently
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('district', 'pin_code', 'state')