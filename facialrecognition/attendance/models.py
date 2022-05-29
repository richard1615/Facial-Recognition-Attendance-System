from datetime import date
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

# Create your models here.

class User(AbstractUser):
    pass

class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=10)
    pic = models.ImageField(upload_to='student_images/')

    class Meta():
        ordering = ['name']

class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student, related_name='courses')
    is_archived = models.BooleanField(default=False)

    class Meta():
        ordering = ['name']

class Class(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='classes')
    topic = models.CharField(max_length=100, default="Something Something" , verbose_name="Topic Taken")
    date = models.DateField(default=date.today)
    time = models.TimeField(default=datetime.now)
    is_active = models.BooleanField(default=True)
    attendancepercentage = models.IntegerField(default=0)

class Attendance(models.Model):
    class_taken = models.ForeignKey(Class, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    time = models.TimeField(null=True)
    status = models.BooleanField(default=False)

    class Meta:
        unique_together = ('class_taken', 'student')