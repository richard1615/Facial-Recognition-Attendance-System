import imp
from unicodedata import name
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    pass

class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_no = models.CharField(max_length=100)
    pic = models.ImageField(upload_to='student_images/')

class Course:
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student)

class Attendance(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.BooleanField()
