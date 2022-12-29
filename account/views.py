from dashboard.views import *
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from account.forms import *
from account.mail_sender import send_code
from account.models import *


def login_code(request):
    context = {'title': 'Verify User'}
    if request.method == 'POST':
        email = request.POST.get('set-email', '')
        isStudent = True if re.search("std\..*ac\.bd$", email) else False
        code = request.POST.get('text', '')
        user = User.objects.get(email=email)
        otp_user = OTP.objects.get(user=user)
        if otp_user.code == code:
            if isStudent:
                return redirect('student-register')
            return redirect('set-password')
        else:
            messages.warning(request, ("Code didn't match"))
            # context['code-error'] = "Code didn't match"
    return render(request, 'login_code.html', context)


def set_password(request):
    context = {'title': 'Set Password'}
    if request.method == 'POST':
        email = request.POST.get('set-email', '')
        pass1 = request.POST.get('password1', '')
        pass2 = request.POST.get('password2', '')

        user = User.objects.get(email=email)
        if pass1 == pass2:
            user.set_password(pass1)
            user.save()
        else:
            messages.warning(request, ("Passwords didn't match"))
            # context['pass-error'] = "passwords didn't match"
            render(request, 'set_password.html', context)

        user = authenticate(request, username=email, password=pass1)
        if user is not None:
            login(request, user)
            return redirect('dashboard-page')
        else:
            # Maybe this section has some problems
            pass
            # messages.warning(request, ("System Fail. Try Again!"))
            # context['error'] = 'System Fail. Try Again!'

    return render(request, 'set_password.html', context)


def student_register_page(request):
    context = {'title': 'Sign Up'}

    if request.method == 'POST':
        email = request.POST.get('set-email', '')
        fname = request.POST.get('fname', '')
        lname = request.POST.get('lname', '')
        studentId = request.POST.get('studentId', '')
        department = request.POST.get('department', '')
        password = request.POST.get('password', '')
        phoneNumber = request.POST.get('phoneNumber', '')

        user = User.objects.get(email=email)
        user.first_name = fname
        user.last_name = lname
        user.set_password(password)
        user.save()

        student = Student(user=user, contact_number=phoneNumber,
                          student_id=studentId, department_id=department)
        student.save()

        return redirect('login-page')

    return render(request, 'student_register_page.html', context)


def register_page(request):

    context = {'title': 'Sign Up'}

    if request.method == 'POST':
        email = request.POST.get('email', '')

        if not email.endswith(".ac.bd"):
            messages.warning(request, (email + ' is invalid!'))
            return render(request, 'register_page.html', context)

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            user = User(email=email, username=email)
            user.save()
            # messages.warning(request, (email + ' dosent exist'))
            # return render(request, 'register_page.html', context)

        code = send_code(email)

        try:
            otp_user = OTP.objects.get(user=user)
            otp_user.code = code
            otp_user.save()
        except OTP.DoesNotExist:
            otp_user = OTP.objects.create(user=user, code=code)

        return redirect('login-code')

    return render(request, 'register_page.html', context)


def home(request):
    return render(request, 'home.html')


def search_exam(exam: Exam, key: str):

    key = key.lower()

    if key in str(exam.room_number):
        return True
    if key in str(exam.course).lower():
        return True
    if key in str(exam.supervisor).lower():
        return True

    for teacher in exam.examiners.all():
        if key in teacher.get_name.lower():
            return True

    return False


def search_course(course: Course, key: str):

    key = key.lower()

    if key in str(course.code).lower():
        return True
    if key in str(course.credits).lower():
        return True
    if key in str(course.department).lower():
        return True
    if key in str(course.level).lower():
        return True
    if key in str(course.semester).lower():
        return True
    if key in str(course.name).lower():
        return True

    return False


def search_teacher(teacher: Teacher, key: str):

    key = key.lower()

    if key in str(teacher.get_name).lower():
        return True
    if key in str(teacher.title).lower():
        return True
    if key in str(teacher.department).lower():
        return True
    if key in str(teacher.contact_number).lower():
        return True
    if key in str(teacher.user).lower():
        return True

    return False


def get_searched_value(value, key):
    # if isinstance(value, list):
    new_value = []
    for v in value:
        if isinstance(v, Exam):
            if search_exam(v, key):
                new_value.append(v)
        elif isinstance(v, Course):
            if search_course(v, key):
                new_value.append(v)
        elif isinstance(v, Teacher):
            if search_teacher(v, key):
                new_value.append(v)
        elif re.search(key, str(v), re.IGNORECASE):
            new_value.append(value)

    return None if len(new_value) == 0 else new_value

    # return None


def homepage_search(request):

    context = dict()
    new_context = dict()

    context['events'] = Event.objects.all()
    context['courses'] = Course.objects.all()
    context['teachers'] = Teacher.objects.all()
    context['departments'] = Department.objects.all()

    # print(context['courses'])

    data_found = False
    if request.method == 'POST':
        if 'search' in request.POST:
            search = request.POST.get('search', '')
            for key, value in context.items():
                # print(value, search)
                new_value = get_searched_value(value, search)
                if new_value:
                    data_found = True
                    new_context[key] = new_value

    departments = set()
    for teacher in new_context.get('teachers', []):
        departments.add(teacher.department)

    new_context['departments'] = list(departments)
    new_context['data_found'] = data_found
    # print(new_context)

    return render(request, 'homepage-search.html', new_context)
