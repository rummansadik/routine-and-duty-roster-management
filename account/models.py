import re
from django.db import models
from django.contrib.auth.models import User

from dashboard.models import *

TEACHER_TITLE_CHOICES = [
    ('Professor', 'Professor'),
    ('Associate Professor', 'Associate Professor'),
    ('Assistant Professor', 'Assistant Professor'),
    ('Lecturer', 'Lecturer'),
    ('None', 'None'),
]


def get_profile_pictures_directory(self: 'Teacher', filename: str):
    return f'img/pp/{self.user_id}_{filename}'


class Student(models.Model):

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)

    contact_number = models.CharField(null=False, unique=True, max_length=255)

    student_id = models.CharField(null=False, unique=True, max_length=255)

    department = models.ForeignKey(
        Department, on_delete=models.DO_NOTHING)

    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name


class Teacher(models.Model):

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)

    title = models.CharField(max_length=255, null=False,
                             choices=TEACHER_TITLE_CHOICES, default='None')

    contact_number = models.CharField(null=False, unique=True, max_length=255)

    profile_picture = models.ImageField(
        upload_to=get_profile_pictures_directory, blank=True, null=True)

    department = models.ForeignKey(Department, on_delete=models.DO_NOTHING)

    is_available = models.BooleanField(default=True)

    total_creadits = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)

    def __str__(self) -> str:
        return self.user.first_name + " " + self.user.last_name

    @property
    def get_instance(self):
        return self

    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def check_supervisor(self):
        return self.title == 'Professor' or self.title == 'Associate Professor'


class Dean(models.Model):

    teacher = models.OneToOneField(Teacher, on_delete=models.PROTECT)

    faculty = models.OneToOneField(Faculty, on_delete=models.PROTECT)

    joined = models.DateField()


class Staff(models.Model):

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)

    contact_number = models.CharField(null=False, unique=True, max_length=11)

    profile_picture = models.ImageField(
        upload_to=get_profile_pictures_directory, blank=True, null=True)

    faculty = models.ForeignKey(Faculty, on_delete=models.DO_NOTHING)

    def __str__(self) -> str:
        return self.user.email

    @property
    def get_instance(self):
        return self

    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name


class Routine(models.Model):

    name = models.CharField(max_length=255, null=False, unique=True)

    start_date = models.DateField()

    session = models.IntegerField()

    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    is_approved = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class Exam(models.Model):

    exam_date = models.DateField()

    exam_time = models.TimeField()

    room_number = models.IntegerField()

    faculty = models.ForeignKey(
        Faculty, on_delete=models.DO_NOTHING, related_name='+')

    course = models.ForeignKey(
        Course, on_delete=models.DO_NOTHING, related_name='+')

    examiners = models.ManyToManyField(Teacher, related_name='+')

    supervisor = models.ForeignKey(
        Teacher, on_delete=models.DO_NOTHING, related_name='supervisor')

    routine = models.ForeignKey(
        Routine, on_delete=models.CASCADE, null=False, default=1)

    def __str__(self) -> str:
        return f"{self.course.code}"


class OTP(models.Model):

    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)

    updated = models.DateTimeField(auto_now=True)

    code = models.CharField(max_length=6, null=False)

    def __str__(self) -> str:
        return self.user.email


class Notification(models.Model):

    user = models.ForeignKey(User, models.CASCADE)

    messages = models.CharField(max_length=255, null=False)

    marked_read = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.messages
