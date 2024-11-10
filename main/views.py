from django.shortcuts import render,  redirect
from django.http import HttpResponse
from django.contrib import messages
import csv
import json
from .models import Student,AttendanceRecord
from django.utils import timezone
from datetime import timedelta

from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import localtime

# Create your views here.

def home(request):
    return render(request, "main/index.html")


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
        registration_id.upper()
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
                
                # Check if the student worked for at least 1 minute
                if duration >= timedelta(minutes=1):
                    # Calculate the minutes worked
                    minutes_worked = duration.total_seconds() / 60
                    attendance_record.sign_out_time = sign_out_time
                    attendance_record.minutes_worked = round(minutes_worked)
                    attendance_record.save()

                    # Send email notification to the student
                    send_sign_out_email(student, sign_in_time, sign_out_time, minutes_worked)
                    
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

# Helper function to send email after sign out
def send_sign_out_email(student, sign_in_time, sign_out_time, minutes_worked):
    subject = "Thank you for working in the Idea Lab"
    
    # HTML email content with basic styling and graphics
    html_message = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                padding: 20px;
            }}
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 8px;
                padding: 30px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                text-align: center;
                background-color: #2d87f0;
                padding: 20px;
                border-radius: 8px;
                color: #ffffff;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .content {{
                padding: 20px;
                color: #333;
            }}
            .content p {{
                line-height: 1.6;
            }}
            .footer {{
                text-align: center;
                font-size: 12px;
                color: #888;
                margin-top: 20px;
            }}
            .footer a {{
                color: #2d87f0;
                text-decoration: none;
            }}
            .footer img {{
                width: 80px;
            }}
            .button {{
                display: inline-block;
                background-color: #2d87f0;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1>Thank You for Your Contribution!</h1>
            </div>
            <div class="content">
                <p>Dear {student.full_name},</p>
                <p>We would like to extend our sincere thanks for your valuable time and effort in the Idea Lab on {localtime(sign_in_time).date()}.</p>
                
                <h3>Your Session Details:</h3>
                <ul>
                    <li><strong>Sign-In Time:</strong> {localtime(sign_in_time).strftime('%H:%M')}</li>
                    <li><strong>Sign-Out Time:</strong> {localtime(sign_out_time).strftime('%H:%M')}</li>
                    <li><strong>Total Time Worked:</strong> {round(minutes_worked)} minutes</li>
                </ul>
                
                <p>Your contributions help us improve the lab's environment and support your peers in their projects. We look forward to seeing you again!</p>
                
                <p>Thank you for being an important part of Team Idea Lab.</p>
                <p><a href="https://www.piet.poornima.org/AICTE_IDEA_lab.html" class="button">Visit Idea Lab</a></p>
            </div>
            <div class="footer">
                <img src="../../favicon.png" alt="Team Idea Lab Logo">
                <p>&copy; {localtime(timezone.now()).year} Team Idea Lab. All rights reserved.</p>
                <p>Have questions? <a href="mailto:aicte.idealab@poornima.org">Contact Us</a></p>
            </div>
        </div>
    </body>
    </html>
    """

    recipient_list = [student.email_id]

    # Send the email with both plain text and HTML content
    send_mail(
        subject,
        "This email requires HTML support",  # Fallback plain text message
        settings.EMAIL_HOST_USER,  # Sender's email from settings
        recipient_list,
        fail_silently=False,  # Set to False to raise an error in case of failure
        html_message=html_message,  # HTML content for the email
    )

    
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

        # Convert total time to minutes
        total_minutes = int(total_time.total_seconds() // 60)

        # Only include students who have worked more than 1 minute
        if total_minutes > 1:
            total_hours, total_minutes = divmod(total_minutes, 60)  # Get hours and remaining minutes
            student_data.append({
                'name': student.full_name,
                'registration_id': student.registration_id,
                'total_hours': total_hours,
                'total_minutes': total_minutes
            })

    # Pass the filtered student data to the template for rendering
    return render(request, 'main/display.html', {'student_data': student_data})
def ledger(request):
    records = AttendanceRecord.objects.order_by('-sign_in_time')[:20]
    return render(request, 'main/ledger.html', {'records': records})

def download_data(request):
    if request.method == 'POST':
        # Get the student data and file name from the POST request
        student_data_json = request.POST.get('student_data')
        file_name = request.POST.get('file_name', 'student_data')  # Default to 'student_data' if no name is provided
        student_data = json.loads(student_data_json)

        # Create a CSV file with the student data
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{file_name}.csv"'

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
