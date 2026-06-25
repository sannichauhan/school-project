from django.db import models

class AdmissionInquiry(models.Model):
    parent_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    email_address = models.EmailField()
    student_name = models.CharField(max_length=255)
    class_applying_for = models.CharField(max_length=50)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.class_applying_for}"