from django import forms
from django.contrib.auth.models import User

from account.models import *

TEACHER_TITLE_CHOICES = [
    ('', ''),
    ('Professor', 'Professor'),
    ('Associate Professor', 'Associate Professor'),
    ('Assistant Professor', 'Assistant Professor'),
    ('Lecturer', 'Lecturer'),
    ('None', 'None'),
]


class LoginForm(forms.Form):

    email = forms.EmailField()

    password = forms.PasswordInput()
