import os
import django
import openpyxl

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attendance.settings")  # Replace with your project name
django.setup()

from main.models import Student  # Adjust this import according to your app name

# Load the Excel file
file_path = './sheet2.xlsx'
workbook = openpyxl.load_workbook(file_path)
sheet = workbook.active  # Use the first sheet

# Iterate through the rows and create Student instances
for row in sheet.iter_rows(min_row=2, values_only=True):  # Skip the header row
    full_name, registration_id = row
    if not Student.objects.filter(registration_id=registration_id).exists():  # Check for duplicates
        student = Student(full_name=full_name, registration_id=registration_id)
        student.save()
        print(f"Added student: {full_name}, Registration ID: {registration_id}")
    else:
        print(f"Student with Registration ID {registration_id} already exists. Skipping.")

print("Import completed.")
