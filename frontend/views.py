from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.forms import  AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth import logout

# Create your views here.


def main_home_page(request):
    return render(request, 'home.html')


def login_page(request):
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
    return redirect(login_page)