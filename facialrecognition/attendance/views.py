from datetime import datetime
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
import os
import cv2

from .models import User, Student, Course, Attendance, Class
from .forms import StudentForm, CourseForm, ClassForm
from .facialrecognition import face_match, face_encode

# Create your views here.

last_face = ["", ""]
face_encodings = []


def index(request):
    user = request.user
    if user.is_authenticated:
        user = request.user
        courses = Course.objects.filter(instructor=user)
        return render(
            request,
            "attendance/dashboard.html",
            {"courses": courses, "username": user.username},
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


def delcourse(request, course_id):
    course = Course.objects.get(pk=course_id)
    course.delete()
    return HttpResponseRedirect(reverse("index"))


def course(request, course_id):
    course = Course.objects.get(pk=course_id)
    
    classes = course.classes.all()
    return render(
        request,
        "attendance/course.html",
        {
            "course": course,
            "classes": classes,
        },
    )

def students(request, course_id):
    course = Course.objects.get(pk=course_id)
    students = course.students.all()
    return render(
        request,
        "attendance/students.html",
        {"students": students}
    )

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


def delstudent(request, course_id, student_id):
    student = Student.objects.get(pk=student_id)
    student.delete()
    return HttpResponseRedirect(reverse("course", args=[course_id]))


def addclass(request, course_id):
    course = Course.objects.get(pk=course_id)
    if request.method == "POST":
        form = ClassForm(request.POST)
        if form.is_valid():
            class_data = form.cleaned_data
            class_obj = Class(
                course=course, date=class_data["date"], time=class_data["time"]
            )
            class_obj.save()
            students = course.students.all()
            for student in students:
                attendance = Attendance(
                    student=student, class_taken=class_obj, status=False
                )
                attendance.save()
            return HttpResponseRedirect(reverse("index"))
    class_form = ClassForm()
    return HttpResponseRedirect(reverse("attendance", args=[course_id]))


def markAttendance(request, class_id):
    global last_face
    class_taken = Class.objects.get(pk=class_id)
    students = class_taken.course.students.all()
    index = face_match(face_encodings)
    try:
        student = students[index]
        attendance = Attendance.objects.get(student=student, class_taken=class_taken)
        attendance.present = True
        attendance.time = datetime.now()
        attendance.save()
        last_face = [student]
    except IndexError:
        last_face = [-1]
    return HttpResponseRedirect(reverse("attendance", args=[class_id]))


def attendance(request, class_id):
    global face_encodings
    class_taken = Class.objects.get(pk=class_id)
    course = class_taken.course
    students = class_taken.course.students.all()
    paths = []
    for student in students:
        path = rf"C:/Users/malav/facial-recognition-attendance-system/facialrecognition/{student.pic.url}"
        paths.append(path)
    face_encodings = face_encode(paths)
    return render(
        request,
        "attendance/attendance.html",
        {"class_taken": class_taken, "course": course},
    )

def exportAttendance(request):
    pass
