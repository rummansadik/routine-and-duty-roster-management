from turtle import title
from faker import Faker

import random

import faker
from account.models import *
from django.contrib.auth.models import User

fake = Faker()

faculies = list(Faculty.objects.all())
depts = list(Department.objects.all())
courses = list(Course.objects.all())
users = list(User.objects.all())
teachers = list(Teacher.objects.all())

titles = [
    'Professor',
    'Associate Professor',
    'Assistant Professor',
    'Lecturer',
    'None',
]


def gen_courses():
    for dept in depts:
        for x in range(101, 104):
            course = Course()
            course.code = dept.name + str(x)
            x = random.choices([0.75, 1.5, 2, 3], k=1)[0]
            course.credits = x
            course.department = depts[random.randint(0, len(depts)-1)]
            if x < 2:
                course.is_sessional = True if random.randint(
                    0, 10) >= 5 else False
            course.level = random.randint(1, 5)
            course.semester = ['I', 'II'][random.randint(0, 1)]
            course.name = fake.job()
            course.save()


def gen_users():
    for _ in range(100):
        user = User()
        email = fake.email()
        user.email = email
        user.username = email
        user.password = email
        user.first_name = fake.first_name()
        user.last_name = fake.last_name()
        user.save()


def gen_teachers():
    for _ in range(100):
        teacher = Teacher()
        teacher.user = users[random.randint(0, len(users)-1)]
        teacher.title = titles[random.randint(0, len(titles)-1)]
        teacher.contact_number = fake.phone_number()
        teacher.department = depts[random.randint(0, len(depts)-1)]
        teacher.save()


def gen_routines():
    for _ in range(100):
        routine = Routine()
        routine.exam_date = fake.date()
        routine.exam_time = fake.time()
        routine.room_number = random.randint(101, 999)
        routine.faculty = faculies[random.randint(0, len(faculies)-1)]
        routine.course = courses[random.randint(0, len(courses)-1)]
        routine.supervisor = teachers[random.randint(0, len(teachers)-1)]
