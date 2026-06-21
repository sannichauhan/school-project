# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.conf import settings

from .models import AdmissionInquiry

# =====================================================================
# 1. GENERAL & AUTHENTICATION VIEWS
# =====================================================================

def main_home_page(request):
    return render(request, 'home.html')


def login_page(request):
    is_authenticated = request.user.is_authenticated
    if is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        initial_data = {'username': '', 'password': ''}
        form = AuthenticationForm(initial=initial_data)
        
    return render(request, "login.html", {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login_page')  # URL name use karna zyada behtar approach hai


# =====================================================================
# 2. ADMISSION INQUIRY VIEW
# =====================================================================

def admission_inquiry_view(request):
    if request.method == 'POST':
        # 1. Capture HTML data using input 'name' tags
        parent_name = request.POST.get('parent_name')
        contact_number = request.POST.get('contact_number')
        email_address = request.POST.get('email_address')
        student_name = request.POST.get('student_name')
        class_applying_for = request.POST.get('class_applying_for')
        message = request.POST.get('message')

        # 2. Save data straight to the Database
        inquiry = AdmissionInquiry.objects.create(
            parent_name=parent_name,
            contact_number=contact_number,
            email_address=email_address,
            student_name=student_name,
            class_applying_for=class_applying_for,
            message=message
        )

        # 3. Formulate Notification Email
        # .upper() handles case safety if strings come back lowercase
        class_display = class_applying_for.upper() if class_applying_for else "NOT SPECIFIED"
        subject = f"New Admission Inquiry: {student_name} ({class_display})"
        
        email_message = f"""
        Hello Administration,

        You have received a new admission inquiry form request.

        Parent's Name: {parent_name}
        Contact Number: {contact_number}
        Email Address: {email_address}
        Student's Name: {student_name}
        Class Selected: {class_display}
        
        Additional Notes:
        {message if message else "None Provided"}

        ---
        Automated system update.
        """

        # 4. Trigger the email sendout
        try:
            send_mail(
                subject=subject,
                message=email_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL, email_address], # Notifies both school admin & the applicant
                fail_silently=False,
            )
        except Exception as e:
            print(f"SMTP Server Error: {e}")

        return render(request, 'success.html')

    return render(request, 'admission_form.html')