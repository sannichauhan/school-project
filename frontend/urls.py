from django.urls import path
from .views import main_home_page, login_page

urlpatterns = [
    path('', main_home_page, name="homepage"),
    path('login/', login_page, name="login_page"),
]