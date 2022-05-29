from django import forms
from .models import Student, Class

class CourseForm(forms.Form):
    name = forms.CharField(max_length=100)
    code = forms.CharField(max_length=10)

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'roll_no', 'pic']

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['topic']