from rest_framework import serializers
from .models import StudentClass, Address, Student, Subject, Exam, MarkSheet, Marks



class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    permanent_address = AddressSerializer()
    local_address = AddressSerializer(required=False, allow_null=True)

    class Meta:
        model = Student
        fields = '__all__'

    def create(self, validated_data):
        perm_addr_data = validated_data.pop('permanent_address')
        local_addr_data = validated_data.pop('local_address', None)

        perm_address = Address.objects.create(**perm_addr_data)
        local_address = Address.objects.create(**local_addr_data) if local_addr_data else None
        
        last_student = Student.objects.order_by('-id').first()

        if last_student and last_student.roll_number:
            last_roll = int(last_student.roll_number)
            new_roll = last_roll+1
        else:
            new_roll = 1001

        student = Student.objects.create(
            permanent_address=perm_address,
            local_address=local_address,
            roll_number=new_roll,
            **validated_data
        )
        return student
    
class StudentClassSerializer(serializers.ModelSerializer):

    students = StudentSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = StudentClass
        fields = '__all__'
        
class MarksSerializer(serializers.ModelSerializer):
    total = serializers.ReadOnlyField(source='total_marks')
    class Meta:
        model = Marks
        fields = ['id', 'subject', 'test_marks', 'written_marks', 'total']

class MarkSheetSerializer(serializers.ModelSerializer):
    subject_marks = MarksSerializer(many=True, read_only=True)
    class Meta:
        model = MarkSheet
        fields = ['id', 'student', 'exam', 'student_class', 'subject_marks']
        
        
### implementing serializer for marksheet

class BulkMarkItemSerializer(serializers.Serializer):
    subject_id = serializers.IntegerField()
    test_marks = serializers.IntegerField(min_value=0)
    written_marks = serializers.IntegerField(min_value=0)

class BulkMarksEntrySerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    exam_id = serializers.IntegerField()
    student_class_id = serializers.IntegerField()
    marks_data = BulkMarkItemSerializer(many=True) # List of marks for each subject


### Serializer for marksheet jsion

class TermMarkSerializer(serializers.Serializer):
    """Handles the { "test": 10, "written": 40 } part"""
    test = serializers.IntegerField()
    written = serializers.IntegerField()

class SubjectPerformanceSerializer(serializers.Serializer):
    """Handles the subject name and the dictionary of terms"""
    subject = serializers.CharField()
    # DictField handles "First Term", "Second Term", etc. as keys
    marks = serializers.DictField(
        child=TermMarkSerializer()
    )

class StudentReportCardSerializer(serializers.Serializer):
    """The main wrapper for the whole JSON object"""
    student_name = serializers.CharField()
    admission_class = serializers.CharField()
    subjects = SubjectPerformanceSerializer(many=True)