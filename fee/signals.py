# fee/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from student.models import Student, AcademicSession, StudentEnrollment
from .services import create_fee_schedule_for_student, promote_student_with_ledger, brand_new_enrollment

@receiver(post_save, sender=Student)
def auto_allocate_new_student_fees(sender, instance, created, **kwargs):
    if created or instance.id:
        active_year = AcademicSession.objects.filter(is_active=True).first()
        if active_year:
            create_fee_schedule_for_student(instance, active_year)
            if created:
                brand_new_enrollment(instance, instance.admission_class, instance.session)


@receiver(pre_save, sender=StudentEnrollment)
def auto_ledger_for_promoted_student(sender, instance, **kwargs):
    promote_student_with_ledger(instance.student, instance.to_class, instance.academic_year)
        
@receiver(pre_save, sender=Student)
def auto_allocate_promoted_student_fees(sender, instance, **kwargs):
    if instance.pk:
        previous_state = Student.objects.get(pk=instance.pk)
        if previous_state.current_class != instance.current_class:
            active_year = AcademicSession.objects.filter(is_active=True).first()
            if active_year:
                create_fee_schedule_for_student(instance, active_year)