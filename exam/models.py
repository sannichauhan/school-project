import re

from django.db import models
import datetime

class TimeTable(models.Model):
    school_name = models.CharField(max_length=200, default="NAV CHETANA PUBLIC SCHOOL")
    title = models.CharField(max_length=200, default="Second Unit Test : (Time-Table) 2026-27")
    start_time = models.TimeField(default=datetime.time(8, 15))  # Default 8:15 AM
    end_time = models.TimeField(default=datetime.time(13, 45))   # Default 1:45 PM (13:45)
    notice_text = models.TextField(blank=True, null=True, help_text="Hindi or English notice at bottom")
    logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)

    @property
    def formatted_timing(self):
        """Format 08:15:00 and 13:45:00 to '8:15 AM To 1:45 PM'"""
        start_str = self.start_time.strftime("%I:%M %p").lstrip('0')
        end_str = self.end_time.strftime("%I:%M %p").lstrip('0')
        return f"{start_str} To {end_str}"

    def __str__(self):
        return f"{self.school_name} - {self.title}"


class ClassGroup(models.Model):
    time_table = models.ForeignKey(TimeTable, related_name='class_groups', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text="e.g. Class- LKG/UKG, Class- 1st to 5th")
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']
    
    @property
    def formatted_name(self):
        if not self.name:
            return ""

        def get_ordinal(num_str):
            try:
                num = int(num_str)
                if 11 <= (num % 100) <= 13:
                    suffix = 'th'
                else:
                    suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(num % 10, 'th')
                return f"{num}{suffix}"
            except ValueError:
                return num_str

        # 1. Check range like "1-5" or "1 to 5"
        range_match = re.search(r'(\d+)\s*[-to]+\s*(\d+)', str(self.name), re.IGNORECASE)
        if range_match:
            start_num = get_ordinal(range_match.group(1))
            end_num = get_ordinal(range_match.group(2))
            return f"Class- {start_num} to {end_num}"

        # 2. Check single number like "10"
        single_match = re.search(r'\b(\d+)\b', str(self.name))
        if single_match and 'st' not in self.name and 'th' not in self.name and 'nd' not in self.name and 'rd' not in self.name:
            num = get_ordinal(single_match.group(1))
            return re.sub(r'\b\d+\b', num, str(self.name))

        # 3. Default fallback (Return exact name if no pattern matches)
        return str(self.name)

    def __str__(self):
        return self.name


class ExamDate(models.Model):
    time_table = models.ForeignKey(TimeTable, related_name='dates', on_delete=models.CASCADE)
    date = models.DateField()

    @property
    def day_name(self):
        """Automatically calculates Day from Date (e.g. Monday)"""
        return self.date.strftime("%A") if self.date else ""

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.date} ({self.day_name})"


class ExamSubject(models.Model):
    exam_date = models.ForeignKey(ExamDate, related_name='subjects', on_delete=models.CASCADE)
    class_group = models.ForeignKey(ClassGroup, related_name='subjects', on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=255, help_text="e.g. Hindi(Written)\nHindi(Oral)")
    
    class Meta:
        unique_together = ('exam_date', 'class_group')

    def __str__(self):
        return f"{self.exam_date.date} - {self.class_group.name}: {self.subject_name}"