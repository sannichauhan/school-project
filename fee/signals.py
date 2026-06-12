# fee/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from student.models import Student, AcademicSession
from .services import create_fee_schedule_for_student

@receiver(post_save, sender=Student)
def auto_allocate_new_student_fees(sender, instance, created, **kwargs):
    if created:
        active_year = AcademicSession.objects.filter(is_active=True).first()
        if active_year:
            create_fee_schedule_for_student(instance, active_year)


@receiver(pre_save, sender=Student)
def auto_allocate_promoted_student_fees(sender, instance, **kwargs):
    if instance.pk:
        previous_state = Student.objects.get(pk=instance.pk)
        if previous_state.current_class != instance.current_class:
            active_year = AcademicSession.objects.filter(is_active=True).first()
            if active_year:
                create_fee_schedule_for_student(instance, active_year)