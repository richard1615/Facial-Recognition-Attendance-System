from datetime import datetime
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
import xlwt

from .models import User, Student, Course, Attendance, Class
from .forms import StudentForm, CourseForm, ClassForm
from .utils import message
from .facialrecognition import face_match, face_encode

# Create your views here.

last_face = ["", -1]
face_encodings = []


def index(request):
    user = request.user
    if user.is_authenticated:
        user = request.user
        courses = Course.objects.filter(instructor=user, is_archived=False)
        archived_courses = Course.objects.filter(instructor=user, is_archived=True)
        class_form = CourseForm()
        return render(
            request,
            "attendance/dashboard.html",
            {"courses": courses, "username": user.username, "class_form": class_form, "archived_courses": archived_courses},
        )
    else:
        return render(request, "attendance/login.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "attendance/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "attendance/login.html")

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request,
                "attendance/register.html",
                {"message": "Passwords must match."},
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "attendance/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "attendance/register.html")


@login_required
def addcourse(request):
    user = request.user
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course_data = form.cleaned_data
            course = Course(
                instructor=user, name=course_data["name"], code=course_data["code"]
            )
            course.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = CourseForm()
    return render(request, "attendance/addcourse.html", {"form": form})


@login_required
def delcourse(request, course_id):
    course = Course.objects.get(pk=course_id)
    course.delete()
    return HttpResponseRedirect(reverse("index"))

@login_required
def archive_course(request, course_id):
    course = Course.objects.get(pk=course_id)
    course.is_archived = True
    course.save()
    return HttpResponseRedirect(reverse("index"))

@login_required
def course(request, course_id):
    course = Course.objects.get(pk=course_id)
    class_form = ClassForm()
    classes = course.classes.all()
    return render(
        request,
        "attendance/course.html",
        {
            "course": course,
            "classes": classes,
            "class_form": class_form,
        },
    )

@login_required
def students(request, course_id):
    course = Course.objects.get(pk=course_id)
    students = course.students.all()
    student_form = StudentForm()
    return render(
        request,
        "attendance/students.html",
        {"students": students,
        "course": course,
        "student_form": student_form,}
    )

@login_required
def addstudent(request, course_id):
    course = Course.objects.get(pk=course_id)
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student_data = form.cleaned_data
            student = Student(
                name=student_data["name"],
                roll_no=student_data["roll_no"],
                pic=student_data["pic"],
            )
            student.save()
            course.students.add(student)
            return HttpResponseRedirect(reverse("students", args=[course_id]))
    student_form = StudentForm()
    return render(request, "attendance/addstudent.html", {"student_form": student_form})

@login_required
def delstudent(request, course_id, student_id):
    student = Student.objects.get(pk=student_id)
    student.delete()
    return HttpResponseRedirect(reverse("course", args=[course_id]))

@login_required
def classes(request, course_id):
    course = Course.objects.get(pk=course_id)
    classes = course.classes.all()
    return render(
        request,
        "attendance/classes.html",
        {"classes": classes,
        "course": course,}
    )

@login_required
def addclass(request, course_id):
    course = Course.objects.get(pk=course_id)
    if request.method == "POST":
        form = ClassForm(request.POST)
        if form.is_valid():
            class_data = form.cleaned_data
            class_obj = Class(
                course=course, topic = class_data["topic"]
            )
            class_obj.save()
            students = course.students.all()
            for student in students:
                attendance = Attendance(
                    student=student, class_taken=class_obj, status=False
                )
                attendance.save()
            return HttpResponseRedirect(reverse("attendance", args=[class_obj.id]))
    class_form = ClassForm()
    #return HttpResponseRedirect(reverse("attendance", args=[course_id]))
    return render(request, "attendance/addclass.html", {"class_form": class_form})

@login_required
def markAttendance(request, class_id):
    global last_face
    global face_encodings
    class_taken = Class.objects.get(pk=class_id)
    students = class_taken.course.students.all()
    index = face_match(face_encodings)
    try:
        student = students[index]
        attendance = Attendance.objects.get(student=student, class_taken=class_taken)
        attendance.status = True
        attendance.time = datetime.now()
        attendance.save()
        last_face = [student.name, 1]
    except IndexError:
        last_face[1] = 0
    return HttpResponseRedirect(reverse("attendance", args=[class_id]))

@login_required
def attendance(request, class_id):
    global face_encodings, last_face
    class_taken = Class.objects.get(pk=class_id)
    course = class_taken.course
    students = class_taken.course.students.all()
    paths = []
    face_encodings = []
    alert = message(last_face)
    for student in students:
        path = rf"C:/Users/malav/facial-recognition-attendance-system/facialrecognition/{student.pic.url}"
        paths.append(path)
    face_encodings = face_encode(paths)
    return render(
        request,
        "attendance/attendance.html",
        {"class_taken": class_taken, "course": course, "alert1": alert[0], "alert2": alert[1]
        }, 
    )

@login_required
def exportAttendance(request, class_id):
    response = HttpResponse(content_type="application/ms-excel")
    class_taken = Class.objects.get(pk=class_id)
    response['Content-Disposition'] = 'attachment; filename=attendance' + \
        str(class_taken.course.name) + '.' + str(class_taken.date) + '.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Attendance')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Name', 'Roll No', 'Present', 'Time']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    attendance_list = Attendance.objects.filter(class_taken=class_taken)

    rows = []

    for attendance in attendance_list:
        present = "Present" if attendance.status else "Absent"
        rows.append(
            [
                attendance.student.name,
                attendance.student.roll_no,
                present,
                str(attendance.time),
            ]
        )

    for row in rows:
        row_num += 1
        
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)

    return response

def end_session(request, course_id, class_id):
    class_taken = Class.objects.get(pk=class_id)
    #calculate attendance percentage
    attendance_list = Attendance.objects.filter(class_taken=class_taken)
    total_students = class_taken.course.students.all().count()
    present_students = attendance_list.filter(status=True).count()
    percentage = (present_students/total_students)*100
    #update attendance percentage
    class_taken.attendancepercentage = percentage
    #close the class
    class_taken.status = False
    class_taken.save()
    return HttpResponseRedirect(reverse("classes", args=[course_id]))