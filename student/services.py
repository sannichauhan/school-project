from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Student, StudentClass, AcademicSession, StudentAcademicHistory, StudentPromotionLog

def promote_student_list(student_ids, target_class_id, target_session_id, user_name=None):
    """
    Safely promotes a batch of students to the next class and new session,
    optimized with bulk lookups to completely eliminate N+1 queries.
    """
    if not student_ids:
        return 0

    # सुनिश्चित करें कि सभी IDs Integer फॉर्मेट में हों ताकि डिक्शनरी मैपिंग में गड़बड़ न हो
    student_ids = [int(sid) for sid in student_ids]

    # 1. लूप के बाहर टारगेट ऑब्जेक्ट्स और वैलिडेशन फ़ेच करें (सिर्फ 2 क्वेरी)
    target_class = get_object_or_404(StudentClass, pk=target_class_id)
    target_session = get_object_or_404(AcademicSession, pk=target_session_id)
    
    promoted_count = 0

    with transaction.atomic():
        # 2. BULK CHECK: उन छात्रों की IDs निकालें जो इस टारगेट सेशन में पहले से ही मौजूद हैं (डुप्लिकेट प्रिवेंशन)
        already_promoted_ids = set(
            StudentAcademicHistory.objects.filter(
                student_id__in=student_ids,
                session=target_session
            ).values_list('student_id', flat=True)
        )

        # 3. सभी छात्रों के करंट एक्टिव इतिहास रिकॉर्ड्स एक बार में लाएं
        current_records = StudentAcademicHistory.objects.filter(
            student_id__in=student_ids,
            is_active=True
        ).select_related('student', 'session', 'student_class')

        # फ़ास्ट लुकअप के लिए डिक्शनरी मैपिंग {int_id: record_object}
        history_map = {record.student_id: record for record in current_records}

        # 4. जिन छात्रों का कोई एक्टिव इतिहास नहीं है, उनके स्टूडेंट ऑब्जेक्ट्स भी एक ही क्वेरी में निकालें
        missing_history_ids = [sid for sid in student_ids if sid not in history_map and sid not in already_promoted_ids]
        student_objects_map = {}
        if missing_history_ids:
            students = Student.objects.filter(pk__in=missing_history_ids)
            student_objects_map = {s.id: s for s in students}

        # ==================== मुख्य लूप (No Database Hits Inside) ====================
        for student_id in student_ids:
            
            # पहले से प्रमोटेड छात्रों को बिना क्वेरी चलाए स्किप करें
            if student_id in already_promoted_ids:
                continue

            current_record = history_map.get(student_id)

            if current_record:
                # पुराने रिकॉर्ड का स्टेटस बदलें
                current_record.promoted_status = 'PROMOTED'
                current_record.is_active = False
                current_record.save()  # यह सिर्फ इस छात्र के रिकॉर्ड को अपडेट करेगा
                
                # लॉग जनरेट करें
                StudentPromotionLog.objects.create(
                    student=current_record.student,
                    from_session=current_record.session,
                    to_session=target_session,
                    from_class=current_record.student_class,
                    to_class=target_class,
                    promoted_by=user_name
                )
                student_obj = current_record.student
            else:
                # बिना हिस्ट्री वाले छात्रों का ऑब्जेक्ट पहले से तैयार मैप से उठाएं
                student_obj = student_objects_map.get(student_id)
                if not student_obj:
                    continue  # अगर छात्र डेटाबेस में ही नहीं है

            # 5. नया एक्टिव हिस्ट्री रिकॉर्ड बनाएं
            # नोट: यहाँ .create() इस्तेमाल करना सही है क्योंकि यह आपके मॉडल के 
            # कस्टम save() मेथड (रोल नंबर जनरेशन + ओल्ड एक्टिव डिसेबल) को ट्रिगर करेगा।
            StudentAcademicHistory.objects.create(
                student=student_obj,
                session=target_session,
                student_class=target_class,
                is_active=True,
                promoted_status='PENDING'
            )
            
            promoted_count += 1
            
    return promoted_count