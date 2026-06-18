from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StudentFeeAllocation
from .services import create_fee_schedule_for_student

@receiver(post_save, sender=StudentFeeAllocation)
def auto_allocate_fees_on_allocation_save(sender, instance, created, **kwargs):
    """
    Jaise hi kisi student ka structured fee configuration framework link save hoga,
    vahan se pipeline context capture karke direct backend automation trigger karega.
    """
    student = instance.student
    academic_year = instance.academic_year
    
    if student and academic_year:
        create_fee_schedule_for_student(student, academic_year)