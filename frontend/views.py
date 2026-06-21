# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .forms import AdmissionInquiryForm  # Form import kiya

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
        form = AdmissionInquiryForm(request.POST)
        
        if form.is_valid():
            # 1. Database mein save kiya
            form.save()
            
            # 2. Cleaned data nikalna email ke liye
            parent_name = form.cleaned_data['parent_name']
            contact_number = form.cleaned_data['contact_number']
            email_address = form.cleaned_data['email_address']
            student_name = form.cleaned_data['student_name']
            class_applying_for = form.cleaned_data['class_applying_for']
            message = form.cleaned_data['message']

            # 3. Email Sendout Logic
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
            """
            try:
                send_mail(
                    subject=subject,
                    message=email_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL, email_address],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"SMTP Server Error: {e}")

            # 🔴 4. Success Message set karein jo Home page par dikhega
            messages.success(request, "Thank you! Your admission inquiry has been submitted successfully.")
            
            # Wapas home page par hi bhej rahe hain
            return redirect('main_home_page') # Aapke home page ka jo bhi URL name hai yahan likhein
            
        else:
            messages.error(request, "Please correct the errors in the form below.")
            return render(request, 'home.html', {'form': form})

    else:
        form = AdmissionInquiryForm()
        
    return render(request, 'home.html', {'form': form})