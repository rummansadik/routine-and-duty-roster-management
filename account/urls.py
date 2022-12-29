from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from account.views import *

urlpatterns = [
    path('', home, name='home'),
    path('login/', LoginView.as_view(template_name='login_page.html',),
         name='login-page'),
    path('register/', register_page, name='register-page'),
    path('student-register/', student_register_page, name='student-register'),
    path('logout/', LogoutView.as_view(template_name='logout_page.html'),
         name='logout-page'),
    path('login-code/', login_code, name='login-code'),
    path('set-password/', set_password, name='set-password'),
    path('homepage-search/', homepage_search, name='homepage-search'),
]
