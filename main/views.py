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

# views.py

from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Student, AttendanceRecord

def sign_in(request):
    if request.method == 'POST':
        registration_id = request.POST.get('registration_id')
        try:
            student = Student.objects.get(registration_id=registration_id)
            # Check if the student is already signed in
            if AttendanceRecord.objects.filter(student=student, sign_out_time=None).exists():
                # If the student is already signed in, redirect with a message
                return render(request, 'sign_in.html', {'error': 'You are already signed in.'})
            else:
                # Create a new attendance record for sign-in
                AttendanceRecord.objects.create(student=student, sign_in_time=timezone.now())
                return redirect('home')
        except Student.DoesNotExist:
            return render(request, 'sign_in.html', {'error': 'Invalid registration ID.'})
    
    return render(request, 'main/sign_in.html')

def sign_out(request):
    if request.method == 'POST':
        registration_id = request.POST.get('registration_id')
        try:
            student = Student.objects.get(registration_id=registration_id)
            # Check if the student is signed in
            if AttendanceRecord.objects.filter(student=student, sign_out_time=None).exists():
                # Get the latest attendance record for the student
                attendance_record = AttendanceRecord.objects.filter(student=student, sign_out_time=None).latest('sign_in_time')
                # Update the sign-out time
                attendance_record.sign_out_time = timezone.now()
                # Calculate the hours worked
                sign_in_time = attendance_record.sign_in_time
                sign_out_time = attendance_record.sign_out_time
                hours_worked = (sign_out_time - sign_in_time).total_seconds() / 3600  # Convert seconds to hours
                attendance_record.hours_worked = round(hours_worked, 2)  # Round to 2 decimal places
                attendance_record.save()
                return redirect('home')
            else:
                # If the student is not signed in, redirect with a message
                return render(request, 'sign_out.html', {'error': 'You are not signed in.'})
        except Student.DoesNotExist:
            return render(request, 'sign_out.html', {'error': 'Invalid registration ID.'})
    
    return render(request, 'main/sign_out.html')

def ledger(request):
    records = AttendanceRecord.objects.all()
    return render(request, 'main/ledger.html', {'records': records})

