from django.urls import path
from .views import main_home_page

urlpatterns = [
    path('', main_home_page, name="homepage"),
]