from pyexpat.errors import messages

from django.contrib import admin

from fee.models import FeeLedger
from .models import Section, StudentClass, Address, Student, Subject, Exam, MarkSheet, Marks, AcademicSession
from .services import promote_student_list
from .forms import AcademicSessionForm

# --- Inlines for a better UI ---

class AddressInline(admin.StackedInline):
    model = Address
    extra = 0 # Prevents empty extra forms from showing up automatically

class MarksInline(admin.TabularInline):
    model = Marks
    extra = 1
    
    # 1. Fields list me wahi naam aayenge jo niche defined hain
    fields = [
        'subject',
        'test_marks',
        'max_test_marks',
        'written_marks',
        'max_written_marks',
        'display_obtained_total',  # Custom method name
        'display_max_total',       # Custom method name
    ]

    # 2. Jo bhi properties ya custom methods hain, unhe readonly banana zaroori hai
    readonly_fields = [
        'display_obtained_total',
        'display_max_total',
    ]

    # 3. Obtained Total dikhane ke liye custom method
    def display_obtained_total(self, obj):
        if obj.id: # Agar object database me save hai tabhi total dikhaye
            return obj.obtained_total
        return "-"
    display_obtained_total.short_description = "Obtained Total"

    # 4. Max Total dikhane ke liye custom method
    def display_max_total(self, obj):
        if obj.id:
            return obj.max_total
        return "-"
    display_max_total.short_description = "Max Total"


# --- Main Admin Classes ---

@admin.register(StudentClass)
class StudentClassAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    
@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    # एडमिन में ऊपर बनाए गए फॉर्म का ही उपयोग करें (ताकि डेट वैलिडेशन यहाँ भी चले)
    form = AcademicSessionForm
    
    # टेबल लिस्ट व्यू में दिखने वाले कॉलम्स
    list_display = ('name', 'start_date', 'end_date', 'is_active_status')
    
    # किन कॉलम्स पर क्लिक करके खोला जा सकता है
    list_display_links = ('name',)
    
    # साइडबार में क्विक फ़िल्टर लगाने के लिए
    list_filter = ('is_active', 'start_date', 'end_date')
    
    # सर्च बार के लिए फ़ील्ड्स
    search_fields = ('name',)
    
    # एडमिन लिस्ट पेज से ही डायरेक्ट ऐक्टिव/इनऐक्टिव टॉगल करने के लिए
    list_editable = () # यदि आप चाहें तो यहाँ 'is_active' डाल सकते हैं
    
    # नया सेशन बनाते समय दिखने वाले सेक्शन्स (UI Layout)
    fieldsets = (
        ('Session Identity', {
            'fields': ('name', 'is_active'),
            'description': 'Enter the name of the academic year.'
        }),
        ('Duration / Dates', {
            'fields': ('start_date', 'end_date'),
            'description': 'Specify the operational dates for this session.'
        }),
    )

    # UI Improvement: एक्टिव स्टेटस के लिए सुंदर टिक/क्रॉस दिखाने के लिए
    @admin.display(boolean=True, description='Is Active?')
    def is_active_status(self, obj):
        return obj.is_active

class FeeLedgerInline(admin.TabularInline):
    model = FeeLedger
    extra = 0
    readonly_fields = ('paid_amount', 'remaining_amount', 'status')
    
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name','roll_number', 'admission_class', 'contact_number', 'gender', 'created_at', 'current_class', 'current_session')
    list_filter = ('admission_class', 'gender', 'religion')
    search_fields = ('name', 'adhaar_number', 'contact_number')
    actions = ['bulk_promote_to_next_class']
    inlines = [FeeLedgerInline]

    @admin.action(description='Promote selected students to next session')
    def bulk_promote_to_next_class(self, request, queryset):
        # For a production setup, you would typically redirect to an intermediate page 
        # to pick the specific target class/session. Here is a simplified version:
        
        student_ids = list(queryset.values_list('id', flat=True))
        
        # Hardcoded example IDs for demonstration; replace these with dynamic inputs
        try:
            target_class_id = 2   # e.g., ID of 'Grade 2'
            target_session_id = 2 # e.g., ID of '2026-2027'
            
            promote_student_list(
                student_ids=student_ids,
                target_class_id=target_class_id,
                target_session_id=target_session_id,
                user_name=request.user.username
            )
            
            self.message_user(
                request, 
                f"Successfully promoted {len(student_ids)} students.", 
                messages.SUCCESS
            )
        except Exception as e:
            self.message_user(
                request, 
                f"Error during promotion: {str(e)}", 
                messages.ERROR
            )
    
    # Organize fields into sections (Fieldsets)
    fieldsets = (
        ('Personal Info', {
            'fields': ('name', 'student_photo', 'date_of_birth', 'gender', 'religion', 'category', 'adhaar_number', 'pen_number')
        }),
        ('Academic & Contact', {
            'fields': ('admission_class','section', 'contact_number', 'father_name', 'mother_name', 'last_institution', 'session', 'choose_school', 'conveyance_facility','transport_route')
        }),
        ('Addresses', {
            'fields': ('permanent_address', 'local_address')
        }),
        ('Fee Information', {
            'fields': ('fee_type', 'transport_installment_type')
        }),
    )

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_class', 'max_test_marks', 'max_written_marks')
    list_filter = ('student_class',)

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    # 'academic_year' ko badal kar 'academic_session' kar dein
    list_display = ('name', 'academic_session', 'term') 
    
    # Agar aapne list_filter ya search_fields me bhi use kiya hai, toh wahan bhi badlein:
    list_filter = ('academic_session', 'term')
    search_fields = ('name',)

# We register Address separately just in case you need to edit an address independently
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('district', 'pin_code', 'state')

@admin.register(MarkSheet)
class MarkSheetAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'student_class')
    list_filter = ('exam', 'student_class')
    search_fields = ('student__name', 'student__roll_number') # Search bar ke liye (Optional par useful)
    inlines = [MarksInline]  # Ab ye sahi se kaam karega

    




