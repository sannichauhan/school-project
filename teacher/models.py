from django.db import models
from django.core.validators import RegexValidator
from student.models import Address, StudentClass, Subject # Importing from your student app

class Designation(models.Model):
    """e.g., PGT, TGT, PRT, Principal, HOD"""
    title = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.title

class Teacher(models.Model):
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others')]
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), 
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')
    ]

    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='teachers/', blank=True, null=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True)
    
    # Contact & Identity
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=15, 
        validators=[RegexValidator(regex=r'^[6-9]\d{9}$', message="Enter valid 10 digit number")]
    )
    adhaar_number = models.CharField(max_length=12, unique=True)
    pan_number = models.CharField(max_length=10, unique=True, blank=True, null=True)

    # Professional Info
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True)
    joining_date = models.DateField()
    qualification = models.CharField(max_length=200) # e.g., B.Ed, M.Sc Physics
    experience_years = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    # Address Link (Reusing your Address model)
    address = models.OneToOneField(Address, on_delete=models.CASCADE, related_name='teacher_profile')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.designation})"



class ClassTeacherAssignment(models.Model):
    """Assigns a teacher as a 'Class Teacher' for a specific class"""
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE)
    student_class = models.OneToOneField(StudentClass, on_delete=models.CASCADE)
    academic_year = models.CharField(max_length=15, default="2025-2026")

    def __str__(self):
        return f"{self.teacher} is Class Teacher of {self.student_class}"

class SubjectAssignment(models.Model):
    """Assigns teachers to specific subjects in specific classes"""
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='subject_assignments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['subject', 'student_class'] # Only one teacher per subject per class

    def __str__(self):
        return f"{self.teacher} - {self.subject} ({self.student_class})"