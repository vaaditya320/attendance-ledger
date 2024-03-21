from django.shortcuts import render,  redirect
from django.http import HttpResponse
from django.contrib import messages
import time
from .models import Student,AttendanceRecord
from django.utils import timezone

# Create your views here.

def home(request):
    return render(request, "main/index.html")

def verify(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        if password == 'idea@piet':
            messages.info(request, "Verified")
            time.sleep(2)
            return redirect("register")
        else:
            messages.warning(request, "wrong password")
            time.sleep(3)
            return redirect(home)
            
            
    return render(request, "main/verify.html")

def register_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        registration_id = request.POST.get('registration_id')
        
    
        Student.objects.create(full_name=full_name, registration_id=registration_id)
        messages.info(request, "User registered successfully")
        time.sleep(5)
        return redirect("home")
    return render(request, "main/register.html")

def sign_in(request):
    if request.method == 'POST':
        registration_id = request.POST.get('registration_id')
        # Check if the student exists
        try:
            student = Student.objects.get(registration_id=registration_id)
        except Student.DoesNotExist:
            return render(request, 'main/error.html', {'message': 'User does not exist.'})
        # Check if the student already signed in
        if AttendanceRecord.objects.filter(student=student, sign_out_time__isnull=True).exists():
            return render(request, 'main/error.html', {'message': 'You are already signed in.'})
        # Create a new attendance record for sign in
        attendance_record = AttendanceRecord.objects.create(student=student, sign_in_time=timezone.now())
        return HttpResponse("done")
    
    return render(request, 'main/sign_in.html')

def sign_out(request):
    if request.method == 'POST':
        registration_id = request.POST.get('registration_id')
        # Check if the student exists
        try:
            student = Student.objects.get(registration_id=registration_id)
        except Student.DoesNotExist:
            return render(request, 'main/error.html', {'message': 'User does not exist.'})
        # Get the student's current sign-in record
        attendance_record = AttendanceRecord.objects.filter(student=student, sign_out_time__isnull=True).first()
        if not attendance_record:
            return render(request, 'main/error.html', {'message': 'You are not signed in.'})
        # Update sign-out time and calculate hours worked
        attendance_record.sign_out_time = timezone.now()
        time_diff = attendance_record.sign_out_time - attendance_record.sign_in_time
        attendance_record.hours_worked = round(time_diff.total_seconds() / 3600) + 1
        attendance_record.save()
        return HttpResponse("done")
    
    return render(request, 'main/sign_out.html')

def ledger(request):
    records = AttendanceRecord.objects.all()
    return render(request, 'main/ledger.html', {'records': records})

