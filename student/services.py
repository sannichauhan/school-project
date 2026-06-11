from django.db import transaction
from .models import Student, StudentClass, AcademicSession, StudentAcademicHistory, StudentPromotionLog

def promote_student_list(student_ids, target_class_id, target_session_id, user_name=None):
    """
    Safely promotes a batch of students to the next class and new session,
    while archiving their older records cleanly. Wrapped in a transaction 
    so if one fails, none are processed.
    """
    target_class = StudentClass.objects.get(pk=target_class_id)
    target_session = AcademicSession.objects.get(pk=target_session_id)
    
    # Use atomic transaction so all promotions succeed together or fail together
    with transaction.atomic():
        for student_id in student_ids:
            student = Student.objects.get(pk=student_id)
            current_record = student.current_academic_record
            
            if current_record:
                # 1. Update old history status
                current_record.promoted_status = 'PROMOTED'
                current_record.is_active = False
                current_record.save()
                
                # 2. Log transaction
                StudentPromotionLog.objects.create(
                    student=student,
                    from_session=current_record.session,
                    to_session=target_session,
                    from_class=current_record.student_class,
                    to_class=target_class,
                    promoted_by=user_name
                )
                
            # 3. Spawn new active history row
            StudentAcademicHistory.objects.create(
                student=student,
                session=target_session,
                student_class=target_class,
                is_active=True,
                promoted_status='PENDING'
            )