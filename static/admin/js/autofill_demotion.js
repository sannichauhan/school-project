django.jQuery(document).ready(function($) {
    $('#id_student').change(function() {
        var studentId = $(this).val();
        if (!studentId) return;

        $.ajax({
            url: '/students/get-student-details/',
            data: { 'student_id': studentId },
            dataType: 'json',
            success: function(data) {
                if (data.session_id) {
                    $('#id_from_session').val(data.session_id).trigger('change');
                }
                if (data.class_id) {
                    $('#id_from_class').val(data.class_id).trigger('change');
                }
            }
        });
    });
});