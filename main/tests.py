from django.test import TestCase, Client
from django.urls import reverse
from .models import Student
from django.utils import timezone

class StudentModelTest(TestCase):
    def setUp(self):
        # This runs before each test method
        self.student = Student.objects.create(
            name="Test Student",
            email="teststudent@example.com"
        )

    def test_student_creation(self):
        # Test that the student is created correctly
        self.assertEqual(self.student.name, "Test Student")
        self.assertEqual(self.student.email, "teststudent@example.com")
    
    def test_student_string_representation(self):
        # Test string representation, if defined in __str__ method
        self.assertEqual(str(self.student), "Test Student")


class SignInViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = Student.objects.create(
            name="Test Student",
            email="teststudent@example.com"
        )

    def test_sign_in_view_get(self):
        # Test GET request to the sign-in page
        response = self.client.get(reverse('main:sign_in'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/sign_in.html')

    def test_sign_in_view_post(self):
        # Test POST request to the sign-in page
        response = self.client.post(reverse('main:sign_in'), {'student_id': self.student.id})
        self.assertEqual(response.status_code, 302)  # Assuming it redirects after signing in

    def test_sign_in_creates_session(self):
        # Test that a sign-in creates a session record or marks attendance
        self.client.post(reverse('main:sign_in'), {'student_id': self.student.id})
        # Assuming you have a way to check attendance or session records
        self.student.refresh_from_db()
        self.assertTrue(self.student.is_signed_in)  # Modify according to actual field/logic


class SignOutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = Student.objects.create(
            name="Test Student",
            email="teststudent@example.com"
        )
        # Simulate the student signing in first
        self.student.is_signed_in = True
        self.student.sign_in_time = timezone.now()
        self.student.save()

    def test_sign_out_view_post(self):
        # Test POST request to the sign-out page
        response = self.client.post(reverse('main:sign_out'), {'student_id': self.student.id})
        self.assertEqual(response.status_code, 302)  # Assuming it redirects after signing out

    def test_sign_out_updates_student_status(self):
        # Test that sign-out updates student status
        self.client.post(reverse('main:sign_out'), {'student_id': self.student.id})
        self.student.refresh_from_db()
        self.assertFalse(self.student.is_signed_in)  # Modify according to actual field/logic


class EmailUtilityTest(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            name="Test Student",
            email="teststudent@example.com"
        )

    def test_send_sign_out_email(self):
        # Assuming send_sign_out_email is a function to send email on sign-out
        from main.utils import send_sign_out_email
        send_sign_out_email(self.student, timezone.now(), timezone.now(), 120)
        # Check that the email was sent (assuming the function uses Django's send_mail)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Sign-out Confirmation", mail.outbox[0].subject)
