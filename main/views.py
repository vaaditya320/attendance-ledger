from django.shortcuts import render,  redirect
from django.http import HttpResponse
from django.contrib import messages
import time
import csv
import json
from .models import Student,AttendanceRecord
from django.utils import timezone
from datetime import timedelta

# Create your views here.

def home(request):
    return render(request, "main/index.html")

def verify(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        if password == 'idea@piet':
            
            
            return redirect("register")
        else:
            messages.warning(request, "wrong password")
        
            return redirect(verify)
            
            
    return render(request, "main/verify.html")

def register_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        registration_id = request.POST.get('registration_id')
        
    
        Student.objects.create(full_name=full_name, registration_id=registration_id)
        
        
        return redirect("home")
    return render(request, "main/register.html")


def sign_in(request):
    if request.method == 'POST':
        registration_id = request.POST.get('registration_id')
        try:
            student = Student.objects.get(registration_id=registration_id)
            # Check if the student is already signed in
            if AttendanceRecord.objects.filter(student=student, sign_out_time=None).exists():
                # If the student is already signed in, redirect with a message
                messages.warning(request, "You are already logged in")
                return render(request, 'main/sign_in.html', {'error': 'You are already signed in.'})
            else:
                # Create a new attendance record for sign-in
                AttendanceRecord.objects.create(student=student, sign_in_time=timezone.now())
                return redirect('home')
        except Student.DoesNotExist:
            messages.warning(request, "User does not exist")
            return render(request, 'main/sign_in.html', {'error': 'Invalid registration ID.'})
    
    return render(request, 'main/sign_in.html')


def sign_out(request):
    if request.method == 'POST':
        registration_id = request.POST.get('registration_id')
        try:
            student = Student.objects.get(registration_id=registration_id)
            if AttendanceRecord.objects.filter(student=student, sign_out_time=None).exists():
                attendance_record = AttendanceRecord.objects.filter(student=student, sign_out_time=None).latest('sign_in_time')
                sign_in_time = attendance_record.sign_in_time
                sign_out_time = timezone.now()
                duration = sign_out_time - sign_in_time
                if duration >= timedelta(minutes=1):  # Ensuring at least one minute of work
                    # Calculate the minutes worked
                    minutes_worked = duration.total_seconds() / 60
                    attendance_record.sign_out_time = sign_out_time
                    attendance_record.minutes_worked = round(minutes_worked)
                    attendance_record.save()
                    return redirect('home')
                else:
                    messages.warning(request, "You must work for at least one minute before signing out.")
                    return render(request, 'main/sign_out.html', {'error': 'You must work for at least one minute before signing out.'})
            else:
                messages.warning(request, "You are not signed in")
                return render(request, 'main/sign_out.html', {'error': 'You are not signed in.'})
        except Student.DoesNotExist:
            messages.warning(request, "Invalid registration ID")
            return render(request, 'main/sign_out.html', {'error': 'Invalid registration ID.'})
    else:
        return render(request, 'main/sign_out.html')
    
def display(request):
    # Fetch all students from the database
    students = Student.objects.all()

    # Create a list to store total time spent for each student
    student_data = []

    # Calculate total time spent for each student
    for student in students:
        total_time = timedelta()

        # Fetch attendance records for the student
        records = AttendanceRecord.objects.filter(student=student)

        # Calculate total time spent by summing up all durations
        for record in records:
            # Check if minutes_worked is not None
            if record.minutes_worked is not None:
                total_time += timedelta(minutes=int(record.minutes_worked))

        # Convert total time to hours and minutes
        total_minutes = int(total_time.total_seconds() // 60)
        total_hours, total_minutes = divmod(total_minutes, 60)  # Get hours and remaining minutes

        # Add student data to the list
        student_data.append({
            'name': student.full_name,
            'registration_id': student.registration_id,
            'total_hours': total_hours,
            'total_minutes': total_minutes
        })

    # Pass student data to the template for rendering
    return render(request, 'main/display.html', {'student_data': student_data})


def ledger(request):
    records = AttendanceRecord.objects.order_by('-sign_in_time')[:20]
    return render(request, 'main/ledger.html', {'records': records})

def download_data(request):
    if request.method == 'POST':
        # Get the student data from the POST request
        student_data_json = request.POST.get('student_data')
        student_data = json.loads(student_data_json)

        # Create a CSV file with the student data
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="student_data.csv"'

        # Create a CSV writer
        csv_writer = csv.writer(response)
        
        # Write header row
        csv_writer.writerow(['Name', 'Registration ID', 'Total Time Spent (Hours:Minutes)'])

        # Write student data rows
        for student in student_data:
            csv_writer.writerow([
                student['name'],
                student['registration_id'],
                f"{student['total_hours']}:{student['total_minutes']}"
            ])

        return response
    else:
        # If the request method is not POST, render an error page
        return render(request, 'main/error.html', {'error_message': 'Invalid request method.'})