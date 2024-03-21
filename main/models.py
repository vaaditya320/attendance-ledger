from django.db import models

# Create your models here.

class Student(models.Model):
    full_name = models.CharField(max_length=100)
    registration_id = models.CharField(max_length=100, unique=True)
    

    def __str__(self):
        return self.full_name
    
    
    
class AttendanceRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    sign_in_time = models.DateTimeField(blank=True, null=True)
    sign_out_time = models.DateTimeField(blank=True, null=True)
    minutes_worked = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Student: {self.student.full_name}, Registration ID: {self.student.registration_id}"