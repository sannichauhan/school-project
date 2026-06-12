from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Student, StudentClass, AcademicSession, StudentAcademicHistory, StudentPromotionLog

def promote_student_list(student_ids, target_class_id, target_session_id, user_name=None):
    """
    Safely promotes a batch of students to the next class and new session,
    with duplicate prevention and optimized queries.
    """
    if not student_ids:
        return 0

    # 1. Fetch target objects outside the loop (sirf 2 queries)
    target_class = get_object_or_404(StudentClass, pk=target_class_id)
    target_session = get_object_or_404(AcademicSession, pk=target_session_id)
    
    promoted_count = 0

    with transaction.atomic():
        # 2. Fetch all student current history records in one single query (N+1 fixed)
        current_records = StudentAcademicHistory.objects.filter(
            student_id__in=student_ids,
            is_active=True
        ).select_related('student', 'session', 'student_class')

        # Convert to dictionary for fast lookups
        history_map = {record.student_id: record for record in current_records}

        for student_id in student_ids:
            # 3. Duplicate Prevention Check
            # Agar student pehle se target session mein mapped hai, to skip karo (unique_together safe)
            already_promoted = StudentAcademicHistory.objects.filter(
                student_id=student_id,
                session=target_session
            ).exists()
            
            if already_promoted:
                continue

            current_record = history_map.get(int(student_id))

            if current_record:
                # 4. Old record ko update karein
                current_record.promoted_status = 'PROMOTED'
                current_record.is_active = False
                current_record.save()
                
                # 5. Log generate karein
                StudentPromotionLog.objects.create(
                    student=current_record.student,
                    from_session=current_record.session,
                    to_session=target_session,
                    from_class=current_record.student_class,
                    to_class=target_class,
                    promoted_by=user_name
                )
            else:
                # Agar student ka koi purana active record nahi hai, to direct naya banane ke liye
                # hume Student instance chahiye hoga safely
                try:
                    student = Student.objects.get(pk=student_id)
                except Student.DoesNotExist:
                    continue

            # 6. New active history record banayein
            # Yeh aapke model ke custom save() method ko cleanly trigger karega roll_number ke liye
            StudentAcademicHistory.objects.create(
                student=current_record.student if current_record else student,
                session=target_session,
                student_class=target_class,
                is_active=True,
                promoted_status='PENDING'
            )
            
            promoted_count += 1
            
    return promoted_count