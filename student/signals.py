from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StudentDemotionLog, StudentPromotionLog, StudentEnrollment

@receiver(post_save, sender=StudentDemotionLog)
def update_student_on_demotion(sender, instance, created, **kwargs):
    """जब कोई स्टूडेंट डिमोट हो, तो उसका करंट क्लास/सेशन अपडेट करें और history maintain करें"""
    if created:
        student = instance.student
        student.current_class = instance.to_class
        student.session = instance.to_session
        student.save(update_fields=['current_class', 'session'])

        # MultipleObjectsReturned se bachne ke liye update_or_create mein unique fields dein
        StudentEnrollment.objects.update_or_create(
            student=student,
            academic_year=instance.to_session,
            to_class=instance.to_class,
            defaults={
                'from_class': instance.from_class,
                'status': 'WITHDRAWN'
            }
        )

@receiver(post_save, sender=StudentPromotionLog)
def update_student_on_promotion(sender, instance, created, **kwargs):
    """जब कोई स्टूडेंट प्रमोट हो, तो उसका करंट क्लास/सेशन अपडेट करें और history maintain करें"""
    if created:
        student = instance.student
        student.current_class = instance.to_class
        student.session = instance.to_session
        student.save(update_fields=['current_class', 'session'])

        # MultipleObjectsReturned سے bachne ke liye update_or_create mein unique fields dein
        StudentEnrollment.objects.update_or_create(
            student=student,
            academic_year=instance.to_session,
            to_class=instance.to_class,
            defaults={
                'from_class': instance.from_class,
                'status': 'PROMOTED'
            }
        )