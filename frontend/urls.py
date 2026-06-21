from django.urls import path
from .views import main_home_page, login_page, logout_view, admission_inquiry_view

urlpatterns = [
    path('', main_home_page, name="homepage"),
    path('login/', login_page, name="login_page"),
    path('logout/', logout_view, name='logout'),
]