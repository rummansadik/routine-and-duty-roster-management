import mimetypes
import re
import os
from datetime import date
from wsgiref.util import FileWrapper

from account.models import *
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.http import StreamingHttpResponse
from django.shortcuts import redirect, render
from django.views.generic.edit import DeleteView

from dashboard.models import *
from dashboard.routine_creator import *
from dashboard.routine_downloader import *
from dashboard.roaster_downloader import *
from dashboard.admit_downloader import downloader as admit_downloader


def is_dean(user):
    try:
        teacher = Teacher.objects.get(user=user)
    except Teacher.DoesNotExist:
        return None

    deans = Dean.objects.filter(teacher=teacher).order_by('-joined')[:1]
    if len(deans) != 1:
        return None

    return deans[0]


def is_staff(user):
    try:
        staff = Staff.objects.get(user=user)
    except Staff.DoesNotExist:
        return None
    return staff


def is_teacher(user):
    try:
        teacher = Teacher.objects.get(user=user)
    except Teacher.DoesNotExist:
        return None
    return teacher


def is_student(user):
    try:
        student = Student.objects.get(user=user)
    except Student.DoesNotExist:
        return None
    return student


def get_staff(faculty):
    return list(Staff.objects.filter(faculty=faculty))


def get_courses(faculty):
    courses = Course.objects.all()

    selected_courses = []
    for course in courses:
        dept = Department.objects.get(name=course.department)
        if dept.faculty == faculty:
            selected_courses.append(course)

    return selected_courses


def get_routines(faculty):
    return list(Exam.objects.filter(faculty=faculty))


def get_teachers(faculty):
    teachers = Teacher.objects.all()

    selected_teachers = []
    for teacher in teachers:
        dept = Department.objects.get(name=teacher.department)
        if dept.faculty == faculty:
            selected_teachers.append(teacher)

    return selected_teachers


def get_exams(approved_routines, teacher=None):
    past = []
    current = []
    upcomming = []

    today = date.today()
    for routine in approved_routines:
        exams = routine.exam_set.all()
        if teacher:
            exams = filter(lambda exam: teacher in exam.examiners.all()
                           or teacher == exam.supervisor, exams)
        for exam in exams:
            if exam.exam_date == today:
                current.append(exam)
            elif exam.exam_date < today:
                past.append(exam)
            else:
                upcomming.append(exam)

    return current, past, upcomming


def get_notification(user):
    return Notification.objects.filter(user=user, marked_read=False).all()


def get_context(request, full_routine=False):
    faculty_name = None
    user = request.user
    dean = is_dean(user)
    staff = is_staff(user)
    teacher = is_teacher(user)
    student = is_student(user)

    if staff:
        faculty_name = staff.faculty
    elif dean:
        faculty_name = dean.faculty
    elif teacher:
        department = Department.objects.get(name=teacher.department)
        faculty_name = department.faculty.name
    elif student:
        department = Department.objects.get(name=student.department)
        faculty_name = department.faculty.name

    faculty = Faculty.objects.get(name=faculty_name)

    context = {
        'is_staff': (staff != None or dean != None),
        'if_staff': staff is not None,
        'if_dean': dean is not None,
        'user': staff or teacher,
        'notifications': list(get_notification(user)),
    }

    if context['is_staff'] or full_routine:
        approved_routines = Routine.objects.filter(is_approved=True).filter(
            department__in=faculty.department_set.all()).all()
        current, past, upcomming = get_exams(approved_routines)
        context['current_exams'] = current
        context['past_exams'] = past
        context['upcomming_exams'] = upcomming
        routines = Routine.objects.filter(is_approved=False).filter(
            department__in=faculty.department_set.all()).all()
        context['routines'] = routines
        context['approved_routines'] = approved_routines

    if context['is_staff']:
        context['faculty'] = faculty
        context['staffs'] = get_staff(faculty)
        context['courses'] = get_courses(faculty_name)
        context['teachers'] = get_teachers(faculty_name)
        context['departments'] = list(
            Department.objects.filter(faculty=faculty))
        year = date.today().year
        context['year'] = year
        context['events'] = Event.objects.filter(
            start_date__year=year).all()

    elif not full_routine:
        print("Here 3")
        context['faculty'] = faculty
        approved_routines = Routine.objects.filter(is_approved=True).filter(
            department__in=faculty.department_set.all()).all()
        current, past, upcomming = get_exams(approved_routines, teacher)
        context['current_exams'] = current
        context['past_exams'] = past
        context['upcomming_exams'] = upcomming
        context['approved_routines'] = approved_routines

    if student:
        context['is_student'] = student is not None,
        context['student'] = Student.objects.get(user=user)

    return context


def dashboard(request):
    context = get_context(request)
    return render(request, 'dashboard.html', context)


def teacher_page(request):
    context = get_context(request)
    return render(request, 'teacher-section.html', context)


def staff_page(request):
    context = get_context(request)
    return render(request, 'staff-section.html', context)


def course_page(request):
    context = get_context(request)
    return render(request, 'course-section.html', context)


def routine_page(request):
    context = get_context(request)
    return render(request, 'routine-section.html', context)


def event_page(request):
    context = get_context(request)
    return render(request, 'event-section.html', context)


def profile_page(request):
    context = get_context(request)
    return render(request, 'profile-section.html', context)


def full_routine(request):
    context = get_context(request, True)
    return render(request, 'full-routine.html', context)


def add_routine(request):
    context = get_context(request)

    if request.method == 'POST':
        name = request.POST.get('name', '')
        dept = request.POST.get('dept', '')
        level = request.POST.get('level', '')
        semester = request.POST.get('semester', '')
        type = request.POST.get('type', '')
        num_students = request.POST.get('num_students', '')
        start_date = request.POST.get('start_date', '')
        faculty = context['faculty']

        CreateRoutine(name, faculty, dept, level, semester,
                      type == 'LAB', int(num_students), start_date)

        return redirect('dashboard-page')

    LEVEL_CHOICES = ['1', '2', '3', '4']
    SEMESTER_CHOICES = ['I', 'II']
    EXAM_TYPES = ['Theory', 'LAB']

    context['levels'] = LEVEL_CHOICES
    context['semesters'] = SEMESTER_CHOICES
    context['types'] = EXAM_TYPES

    return render(request, 'add-routine.html', context)


def add_staff(request):

    context = get_context(request)

    if request.method == 'POST':
        fname = request.POST.get('first_name', '')
        lname = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        mobile = request.POST.get('mobile', '')
        picture = request.POST.get('picture')
        faculty = context['faculty']

        try:
            with transaction.atomic():
                user = User(
                    username=email,
                    email=email,
                    first_name=fname,
                    last_name=lname,
                )

                user.save()

                staff = Staff.objects.create(
                    user=user,
                    contact_number=mobile,
                    faculty=faculty,
                )

                staff.profile_picture = get_directory(user.id, picture)
                staff.save()

        except:
            return redirect('add-staff')

        return redirect('staff-section')

    return render(request, 'add-staff.html', context)


def get_directory(user_id, filename: str):
    return f'img/pp/{user_id}_{filename}'


def add_teacher(request):

    if request.method == 'POST':
        fname = request.POST.get('first_name', '')
        lname = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        title = request.POST.get('title', '')
        mobile = request.POST.get('mobile', '')
        picture = request.POST.get('picture')
        dept = request.POST.get('dept', '')

        try:
            with transaction.atomic():
                user = User(
                    username=email,
                    email=email,
                    first_name=fname,
                    last_name=lname,
                )

                user.save()

                teacher = Teacher.objects.create(
                    user=user,
                    title=title,
                    contact_number=mobile,
                    department=Department.objects.get(name=dept)
                )

                teacher.profile_picture = get_directory(user.id, picture)
                teacher.save()

        except:
            return redirect('add-teacher')

        return redirect('teacher-section')

    TEACHER_TITLE_CHOICES = [
        'Professor', 'Associate Professor', 'Assistant Professor', 'Lecturer', 'None']

    context = get_context(request)
    context['titles'] = TEACHER_TITLE_CHOICES

    return render(request, 'add-teacher.html', context)


def edit_teacher(request):
    context = get_context(request)
    return render(request, 'edit-teacher.html', context)


def edit_staff(request):
    context = get_context(request)
    return render(request, 'edit-staff.html', context)


class TeacherDeleteView(DeleteView):
    model = Teacher
    success_url = '/'
    template_name = 'teacher_confirm_delete.html'


class StaffDeleteView(DeleteView):
    model = Staff
    success_url = '/'
    template_name = 'staff_confirm_delete.html'


class EventDeleteView(DeleteView):
    model = Event
    success_url = '/'
    template_name = 'event_confirm_delete.html'


class CourseDeleteView(DeleteView):
    model = Course
    success_url = '/'
    template_name = 'course_confirm_delete.html'


def add_event(request):
    context = get_context(request)

    if request.method == 'POST':
        name = request.POST.get('name', '')
        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')
        notes = request.POST.get('notes', '')
        event = Event.objects.create(
            name=name,
            start_date=start_date,
            end_date=end_date,
            notes=notes,
        )
        event.save()
        return render(request, 'event-section.html', context)
    return render(request, 'add-event.html', context)


def edit_event(request):
    context = get_context(request)

    if request.method == 'POST':
        name = request.POST.get('name', '')
        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')
        notes = request.POST.get('notes', '')
        event = Event.objects.create(
            name=name,
            start_date=start_date,
            end_date=end_date,
            notes=notes,
        )
        event.save()
        return render(request, 'event-section.html', context)
    return render(request, 'add-event.html', context)


def add_course(request):
    context = get_context(request)

    if request.method == 'POST':
        level = request.POST.get('level', '')
        semester = request.POST.get('semester', '')
        code = request.POST.get('code', '')
        course_title = request.POST.get('name', '')
        credit = request.POST.get('credits', '')
        course_type = request.POST.get('is_sessional', '')
        course = Course.objects.create(
            level=level,
            semester=semester,
            code=code,
            name=course_title,
            credits=credit,
            is_sessional=course_type,
        )
        course.save()
        return render(request, 'course-section.html', context)
    return render(request, 'add-course.html', context)


def edit_course(request):
    context = get_context(request)

    if request.method == 'POST':
        name = request.POST.get('name', '')
        start_date = request.POST.get('start_date', '')
        end_date = request.POST.get('end_date', '')
        notes = request.POST.get('notes', '')
        event = Event.objects.create(
            name=name,
            start_date=start_date,
            end_date=end_date,
            notes=notes,
        )
        event.save()
        return render(request, 'course-section.html', context)
    return render(request, 'edit-course.html', context)


def dean_view_pending_routine(request):
    context = get_context(request)
    return render(request, 'dean_view_pending_routine.html', context)


def routine_view(request, pk):
    context = get_context(request)
    routine = Routine.objects.filter(pk=pk).first()
    exams = Exam.objects.filter(routine=routine).all()
    context['exams'] = exams
    context['routine_name'] = routine.name
    return render(request, 'routine_view.html', context)


def routine_approve_view(request, pk):
    context = get_context(request)
    routine = Routine.objects.filter(pk=pk).first()
    exams = Exam.objects.filter(routine=routine).all()
    context['exams'] = exams
    context['routine_name'] = routine.name
    context['routine_id'] = routine.id
    return render(request, 'routine-approve-view.html', context)


def approve_routine_view(request, pk):
    context = get_context(request)
    routine = Routine.objects.get(id=pk)
    routine.is_approved = True

    routine.save()
    return render(request, 'dashboard.html', context)


def reject_routine_view(request, pk):
    context = get_context(request)
    routine = Routine.objects.get(id=pk)
    routine.delete()
    return render(request, 'dashboard.html', context)


def marked_notification(request, pk):
    notification = Notification.objects.get(pk=pk)
    notification.marked_read = True
    notification.save()
    return redirect('dashboard-page')


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
    if isinstance(value, list):
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

    return None


def search_page(request):

    context = get_context(request)

    new_context = dict()
    new_context['is_staff'] = context['is_staff']
    new_context['if_staff'] = context['if_staff']
    new_context['if_dean'] = context['if_dean']
    new_context['user'] = context['user']
    new_context['notifications'] = context['notifications']
    new_context['faculty'] = context['faculty']

    data_found = False
    if request.method == 'POST':
        if 'search' in request.POST:
            search = request.POST.get('search', '')
            for key, value in context.items():
                new_value = get_searched_value(value, search)
                if new_value:
                    data_found = True
                    new_context[key] = new_value

    departments = set()
    for teacher in new_context.get('teachers', []):
        departments.add(teacher.department)

    new_context['departments'] = list(departments)
    new_context['data_found'] = data_found

    return render(request, 'search-page.html', new_context)


def download_routine(request, name):
    routine = Routine.objects.get(name=name)
    exams = Exam.objects.filter(routine=routine)
    downloader(exams, routine, exams[0].room_number, exams[0].exam_time)

    base_dir = settings.BASE_DIR
    file = os.path.join(base_dir, 'Sample/output.pdf')
    chunk_size = 8192

    f = FileWrapper(open(file, 'rb'), chunk_size)
    response = StreamingHttpResponse(
        f, content_type=mimetypes.guess_type(file)[0])
    response['Content-Length'] = os.path.getsize(file)
    response['Content-Disposition'] = "Attachment;filename=%s" % name

    return response


def download_admit(request, name):
    routine = Routine.objects.get(name=name)
    student = is_student(request.user)
    if student == None:
        redirect("dashboard-page")

    admit_downloader(routine, student)

    base_dir = settings.BASE_DIR
    file = os.path.join(base_dir, 'Sample/Admit.pdf')
    chunk_size = 8192

    f = FileWrapper(open(file, 'rb'), chunk_size)
    response = StreamingHttpResponse(
        f, content_type=mimetypes.guess_type(file)[0])
    response['Content-Length'] = os.path.getsize(file)
    response['Content-Disposition'] = "Attachment;filename=%s" % name

    return response


def download_roaster(request, name):
    routine = Routine.objects.get(name=name)
    exams = Exam.objects.filter(routine=routine)

    roaster(exams, routine)

    base_dir = settings.BASE_DIR
    file = os.path.join(base_dir, f"Sample/Roaster/{name}.docx")
    chunk_size = 8192

    f = FileWrapper(open(file, 'rb'), chunk_size)
    response = StreamingHttpResponse(
        f, content_type=mimetypes.guess_type(file)[0])
    response['Content-Length'] = os.path.getsize(file)
    response['Content-Disposition'] = "Attachment;filename=%s" % name

    return response
