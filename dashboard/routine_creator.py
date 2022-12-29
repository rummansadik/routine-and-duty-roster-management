import datetime
import math

from account.models import *

from dashboard.models import *

available_teachers = Teacher.objects.filter(is_available=True)


def get_teachers(faculty_name):
    faculty = Faculty.objects.get(name=faculty_name)
    departments = faculty.department_set.all()
    teachers = available_teachers.filter(department__in=departments)

    examiners = []
    supervisors = []

    for teacher in teachers:
        if teacher.check_supervisor:
            supervisors.append(teacher)
        else:
            examiners.append(teacher)

    examiners = sorted(examiners, key=lambda t: t.total_creadits)
    supervisors = sorted(supervisors, key=lambda t: t.total_creadits)

    return supervisors, examiners


def get_date(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()


def get_next_date(cur_date, delta=1):
    return cur_date + datetime.timedelta(days=delta)


def get_next_events(cur_date):
    return Event.objects.filter(start_date__lte=cur_date, end_date__gte=cur_date).all()


def get_next_exams(cur_date, room, shift):
    return Exam.objects.filter(exam_date=cur_date, room_number=room, exam_time=shift).all()


def get_available_date(cur_date, room, shift):

    if cur_date.weekday() == 4:
        cur_date = get_next_date(cur_date)

    if cur_date.weekday() == 5:
        cur_date = get_next_date(cur_date)

    events = get_next_events(cur_date)
    exams = get_next_exams(cur_date, room, shift)
    if len(events) == 0 and len(exams) == 0:
        return cur_date

    if len(events) != 0:
        cur_date = events[0].end_date
    cur_date = get_next_date(cur_date)

    return get_available_date(cur_date, room, shift)


def get_end_date(cur_date, room, shift, courses: Course):

    best_end = None
    best_courses = []

    for i in range(len(courses)):
        x = i
        step = len(courses)
        vis = [False] * step
        cur = get_available_date(cur_date, room, shift)

        new_courses = []
        while(step > 0):
            step -= 1
            vis[x] = True
            new_courses.append(courses[x])

            y = None
            end_date = None
            for j in range(len(courses)):
                if vis[j] == False:
                    delta = int(math.ceil(courses[j].credits))
                    now_date = get_next_date(cur, delta)
                    now_date = get_available_date(now_date, room, shift)
                    if not end_date or now_date < end_date:
                        y = j
                        end_date = now_date

            if not y:
                x = y
                cur = end_date

        if not best_end or cur < best_end:
            best_end = cur
            best_courses = new_courses

    return best_end, best_courses


def get_best_info(start_date, courses: Course):
    rooms = Room.objects.all()
    shifts = Shift.objects.all()

    best_room = None
    best_shift = None
    best_end_date = None

    new_courses = []
    courses = sorted(courses, key=lambda c: c.credits)

    for room in rooms:
        for shift in shifts:
            cur_date = start_date
            end_date, _courses = get_end_date(
                cur_date, room.room_no, shift.time, courses)
            if (not best_end_date) or (best_end_date > end_date):
                best_room = room.room_no
                best_shift = shift.time
                best_end_date = end_date
                new_courses = courses

    return best_room, best_shift, new_courses


def CreateRoutine(routine_name, faculty_name, department_name,
                  level, semester, exam_type, num_students, date_str):

    faculty = Faculty.objects.get(name=faculty_name)
    supervisors, examiners = get_teachers(faculty_name)
    department = Department.objects.get(name=department_name)

    courses = department.course_set.filter(
        level=level, semester=semester, is_sessional=exam_type)

    start_date = get_date(date_str)

    routine = Routine()
    routine.name = routine_name
    routine.department = department
    routine.start_date = start_date
    routine.is_approved = False
    routine.save()

    room, shift, courses = get_best_info(start_date, courses)

    cur_date = get_date(date_str)
    need_examiners = max(2, (num_students-5) // 15)

    for course in courses:

        exam = Exam()

        cur_date = get_available_date(cur_date, room, shift)
        exam.exam_date = cur_date
        cur_date = get_next_date(cur_date, (int)(course.credits))

        exam.exam_time = shift

        exam.room_number = room

        exam.faculty = faculty

        exam.course = course

        exam.supervisor = supervisors[0]
        notification = Notification()
        notification.user = supervisors[0].user
        notification.messages = f"You are assigned as a supervisor in {course.code}"
        notification.save()

        supervisors[0].total_creadits += course.credits

        exam.routine = routine

        exam.save()

        for _ in range(need_examiners):
            exam.examiners.add(examiners[_])
            examiners[_].total_creadits += course.credits

            notification = Notification()
            notification.user = examiners[_].user
            notification.messages = f"You are assigned as a examiner in {course.code}"
            notification.save()

        examiners = sorted(examiners, key=lambda t: t.total_creadits)
        supervisors = sorted(supervisors, key=lambda t: t.total_creadits)
