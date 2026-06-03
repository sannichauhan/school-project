from rest_framework import serializers

from student.models import Address
from .models import Teacher, Designation, ClassTeacherAssignment, SubjectAssignment
from student.serializers import AddressSerializer

class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = '__all__'

class TeacherSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    designation_name = serializers.ReadOnlyField(source='designation.title')

    class Meta:
        model = Teacher
        fields = '__all__'

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        address_inst = Address.objects.create(**address_data)
        return Teacher.objects.create(address=address_inst, **validated_data)

class SubjectAssignmentSerializer(serializers.ModelSerializer):
    teacher_name = serializers.ReadOnlyField(source='teacher.first_name')
    subject_name = serializers.ReadOnlyField(source='subject.name')
    class_name = serializers.ReadOnlyField(source='student_class.name')

    class Meta:
        model = SubjectAssignment
        fields = '__all__'
        
class ClassTeacherAssignmentSerializer(serializers.ModelSerializer):
    teacher_name = serializers.ReadOnlyField(source='teacher.first_name')
    class_name = serializers.ReadOnlyField(source='student_class.name')

    class Meta:
        model = ClassTeacherAssignment
        fields = '__all__'

# (The SubjectAssignmentSerializer from the previous step goes here too)