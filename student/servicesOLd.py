from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import StudentClass, Student, StudentEnrollment, AcademicSession
from fee.models import FeeLedger 

def bulk_promote_students_with_ledger(academic_year_id, from_class_id=None, student_ids=None):
    target_session = get_object_or_404(AcademicSession, id=academic_year_id)
    
    if from_class_id and not student_ids:
        current_class = get_object_or_404(StudentClass, id=from_class_id)
        students_to_promote = Student.objects.filter(current_class=current_class)
    elif student_ids:
        students_to_promote = Student.objects.filter(id__in=student_ids)
    else:
        raise ValueError("Class or student IDs must be provided.")

    all_classes = list(StudentClass.objects.order_by('serial'))
    
    enrollments_to_create = []
    students_to_update = []
    old_enrollments_to_deactivate = []
    ledgers_to_create = []

    with transaction.atomic():
        for student in students_to_promote:
            current_class = student.current_class
            
            next_class = None
            if current_class:
                try:
                    current_index = all_classes.index(current_class)
                    if current_index + 1 < len(all_classes):
                        next_class = all_classes[current_index + 1]
                except ValueError:
                    pass

            previous_dues = 0.00
            current_enrollment = StudentEnrollment.objects.filter(
                student=student, is_active=True
            ).first()

            if current_enrollment:
                old_session = current_enrollment.academic_year
                unpaid_ledgers = FeeLedger.objects.filter(
                    student=student,
                    academic_year=old_session,
                    status__in=['PENDING', 'PARTIALLY_PAID']
                )
                for ledger in unpaid_ledgers:
                    previous_dues += float(ledger.remaining_amount)
                
                current_enrollment.is_active = False
                old_enrollments_to_deactivate.append(current_enrollment)

            exists = StudentEnrollment.objects.filter(
                student=student, academic_year=target_session, from_class=current_class, to_class=next_class
            ).exists()

            if not exists:
                enrollments_to_create.append(
                    StudentEnrollment(
                        student=student,
                        from_class=current_class,
                        to_class=next_class,
                        academic_year=target_session,
                        status='PROMOTED' if next_class else 'GRADUATED',
                        is_active=True
                    )
                )

                if previous_dues > 0:
                    ledgers_to_create.append(
                        FeeLedger(
                            student=student,
                            academic_year=target_session,
                            installment_number=0,
                            category='ACADEMIC',
                            description="Carried Forward Dues",
                            total_amount=previous_dues,
                            due_date=timezone.now(),
                            status='PENDING'
                        )
                    )

                student.session = target_session
                student.current_class = next_class
                students_to_update.append(student)

        if old_enrollments_to_deactivate:
            StudentEnrollment.objects.bulk_update(old_enrollments_to_deactivate, fields=['is_active'])
            
        if enrollments_to_create:
            StudentEnrollment.objects.bulk_create(enrollments_to_create)
            
        if students_to_update:
            Student.objects.bulk_update(students_to_update, fields=['session', 'current_class'])
            
        if ledgers_to_create:
            FeeLedger.objects.bulk_create(ledgers_to_create)

        # from fee.signals import auto_ledger_for_promoted_student
        # for enrollment in enrollments_to_create:
        #     # Signal function ko manually call kar rahe hain bypass/bulk ke baad aur recursion ka dar bhi nahi hai
        #     auto_ledger_for_promoted_student(sender=StudentEnrollment, instance=enrollment, created=True)

    return len(enrollments_to_create)