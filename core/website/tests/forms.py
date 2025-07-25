from django.test import TestCase

from website.forms import ContactForm, NewsLetterForm


class ContactFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.valid_data = {
            "full_name": "My full name",
            "email": "user@gmail.com",
            "phone_number": "+989999999999",
            "subject": "My subject",
            "content": "My content",
        }

    def test_form_with_valid_data(self):
        form = ContactForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_with_invalid_data(self):
        invalid_data = self.valid_data.copy()
        invalid_data["subject"] = ""
        form = ContactForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("subject", form.errors)
        self.assertIn("This field is required.", form.errors["subject"])


class NewsLetterFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.valid_data = {
            "email": "user@gmail.com",
        }

    def test_form_with_valid_data(self):
        form = NewsLetterForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_with_invalid_data(self):
        invalid_data = self.valid_data.copy()
        invalid_data["email"] = ""
        form = NewsLetterForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertIn("This field is required.", form.errors["email"])
