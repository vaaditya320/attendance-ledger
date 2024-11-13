import os
import django
import openpyxl

# Set up Django environment
# This is necessary to set up Django when running this script outside of the Django development server
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attendance.settings")  # Replace 'attendance' with your Django project name
django.setup()

# Import the Student model from the 'main' app
from main.models import Student  # Adjust this import according to your app name

# Load the Excel file
file_path = './data.xlsx'  # Path to the Excel file containing student data
workbook = openpyxl.load_workbook(file_path)  # Open the Excel workbook
sheet = workbook.active  # Get the active sheet (the first sheet by default)

# Iterate through the rows in the sheet (starting from row 2 to skip the header)
for row in sheet.iter_rows(min_row=2, values_only=True):  # Skip the header row
    # Remove any empty or None values from the row (useful for cases where there are empty cells)
    row = [value for value in row if value]  # Filter out empty cells
    if len(row) == 3:  # Check if the row contains exactly 3 values: Registration ID, Full Name, and Email Id
        registration_id, full_name, email_id = row  # Unpack the values into respective variables
        # Check if the student with the given registration_id already exists in the database
        if not Student.objects.filter(registration_id=registration_id).exists():  # Avoid duplicates
            # If the student doesn't exist, create a new Student instance and save it
            student = Student(full_name=full_name, registration_id=registration_id, email_id=email_id)
            student.save()  # Save the student to the database
            print(f"Added student: {full_name}, Registration ID: {registration_id}, Email: {email_id}")
        else:
            # If the student already exists, print a message and skip
            print(f"Student with Registration ID {registration_id} already exists. Skipping.")
    else:
        # If the row doesn't have 3 values, print a message indicating it's being skipped
        print(f"Skipping row with incorrect number of values: {row}")

# Print a message when the import is complete
print("Import completed.")