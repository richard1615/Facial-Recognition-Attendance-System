from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("addcourse/", views.addcourse, name="addcourse"),
    path("delcourse/<int:course_id>", views.delcourse, name="delcourse"),
    path("students/<int:course_id>", views.students, name="students"),
    path("course/<int:course_id>", views.course, name="course"),
    path("classes/<int:course_id>", views.classes, name="classes"),
    path(
        "delstudent/<int:course_id>/<int:student_id>",
        views.delstudent,
        name="delstudent",
    ),
    path("addclass/<int:course_id>", views.addclass, name="addclass"),
    path("attendance/<int:class_id>", views.attendance, name="attendance"),
    path("markattendance/<int:class_id>", views.markAttendance, name="markattendance"),
    path("export_excel/<int:class_id>", views.exportAttendance, name="export_excel"),
]
