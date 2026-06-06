from django.shortcuts import render

# Create your views here.


def main_home_page(request):
    return render(request, 'home.html')