# fee/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from student.models import Student, AcademicSession, StudentEnrollment
from .services import create_fee_schedule_for_student, promote_student_with_ledger, brand_new_enrollment

@receiver(post_save, sender=Student)
def auto_allocate_new_student_fees(sender, instance, created, **kwargs):
    # Yeh naye student ke liye aur update hone par dono par chalega
    if created or instance.id:
        # Student ke session ke hisaab se fee schedule / transport check karega
        session_to_use = instance.session or AcademicSession.objects.filter(is_active=True).first()
        if session_to_use:
            create_fee_schedule_for_student(instance, session_to_use)
            
        if created:
            brand_new_enrollment(instance, instance.admission_class, instance.session)


@receiver(post_save, sender=StudentEnrollment)
def auto_ledger_for_promoted_student(sender, instance, created, **kwargs):
    if created:
        create_fee_schedule_for_student(instance.student, instance.academic_year)
         
@receiver(pre_save, sender=Student)
def auto_allocate_promoted_student_fees(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous_state = Student.objects.get(pk=instance.pk)
            # Agar Class ya Transport Route / Facility change hui hai toh active session par schedule update karein
            if (previous_state.current_class != instance.current_class or 
                previous_state.transport_route != instance.transport_route or
                previous_state.conveyance_facility != instance.conveyance_facility or
                previous_state.transport_installment_type != instance.transport_installment_type):
                
                active_year = instance.session or AcademicSession.objects.filter(is_active=True).first()
                if active_year:
                    create_fee_schedule_for_student(instance, active_year)
        except Student.DoesNotExist:
            pass


# from django.db.models.signals import post_save, pre_save
# from django.dispatch import receiver
# from student.models import Student, AcademicSession, StudentEnrollment
# from .services import create_fee_schedule_for_student, promote_student_with_ledger, brand_new_enrollment

# @receiver(post_save, sender=Student)
# def auto_allocate_new_student_fees(sender, instance, created, **kwargs):
#     if created or instance.id:
#         # active_year = AcademicSession.objects.filter(is_active=True).order_by('start_date').first()
#         create_fee_schedule_for_student(instance, instance.session)
#         if created:
#             brand_new_enrollment(instance, instance.admission_class, instance.session)


# @receiver(post_save, sender=StudentEnrollment)
# def auto_ledger_for_promoted_student(sender, instance, created, **kwargs):
#     #  promote_student_with_ledger(instance.student, instance.to_class, instance.academic_year)
#     if created:
#         create_fee_schedule_for_student(instance.student, instance.academic_year)
        
# @receiver(pre_save, sender=Student)
# def auto_allocate_promoted_student_fees(sender, instance, **kwargs):
#     if instance.pk:
#         previous_state = Student.objects.get(pk=instance.pk)
#         if previous_state.current_class != instance.current_class:
#             active_year = AcademicSession.objects.filter(is_active=True).first()
#             if active_year:
#                 create_fee_schedule_for_student(instance, active_year)