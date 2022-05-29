from django.contrib import admin

# Register your models here.

from .models import User, Student, Course, Attendance, Class

admin.site.register(User)
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Attendance)
admin.site.register(Class)
