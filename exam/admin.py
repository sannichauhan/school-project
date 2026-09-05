from django.contrib import admin
from .models import TimeTable, ClassGroup, ExamDate, ExamSubject


class ClassGroupInline(admin.TabularInline):
    model = ClassGroup
    extra = 1


class ExamDateInline(admin.TabularInline):
    model = ExamDate
    extra = 1


class ExamSubjectInline(admin.TabularInline):
    model = ExamSubject
    extra = 1


@admin.register(TimeTable)
class TimeTableAdmin(admin.ModelAdmin):
    # 'timing' ki jagah 'formatted_timing' property aur start/end time use kiya gaya hai
    list_display = ('school_name', 'title', 'formatted_timing', 'start_time', 'end_time')
    inlines = [ClassGroupInline, ExamDateInline]


@admin.register(ExamDate)
class ExamDateAdmin(admin.ModelAdmin):
    # day_name ab property hai, use display function dwara call kiya gaya hai
    list_display = ('date', 'get_day_name', 'time_table')
    inlines = [ExamSubjectInline]

    @admin.display(description='Day')
    def get_day_name(self, obj):
        return obj.day_name


admin.site.register(ClassGroup)
admin.site.register(ExamSubject)