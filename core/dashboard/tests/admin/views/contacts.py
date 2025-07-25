from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserType
from website.models import ContactModel

User = get_user_model()


class AdminContactListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.contact1 = ContactModel.objects.create(
            full_name="Test User 1",
            email="testuser1@example.com",
            phone_number="09123456789",
            subject="Test Subject 1",
            content="Test Content 1",
        )
        cls.contact2 = ContactModel.objects.create(
            full_name="Test User 2",
            email="testuser2@example.com",
            phone_number="09876543210",
            subject="Test Subject 2",
            content="Test Content 2",
        )
        cls.user = User.objects.create_user(
            email="test@example.com", password="Test123/"
        )
        cls.admin = User.objects.create_user(
            email="admin@example.com",
            password="Admin123/",
            type=UserType.admin.value,
        )
        cls.url = reverse("dashboard:admin:contact-list")

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_customer_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_admin_user(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.contact1.subject)

    def test_search_functionality(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url + "?q=testuser1@example.com")
        self.assertContains(response, "Test Subject 1")
        self.assertNotContains(response, "Test Subject 2")

        self.client.get(self.url + "?q=Test Subject 1")
        self.assertContains(response, "Test Subject 1")


class AdminContactDetailViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="test@example.com", password="Test123/"
        )
        cls.admin = User.objects.create_user(
            email="admin@example.com",
            password="Admin123/",
            type=UserType.admin.value,
        )

    def setUp(self):
        self.contact = ContactModel.objects.create(
            full_name="Test User",
            email="testuser1@example.com",
            phone_number="09123456789",
            subject="Test Subject",
            content="Test Content",
        )
        self.url = reverse(
            "dashboard:admin:contact-detail", args=[self.contact.pk]
        )

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_customer_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_admin_user(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.contact.subject)
        self.assertContains(response, self.contact.content)

    def test_change_is_seen_to_true(self):
        self.client.force_login(self.admin)
        self.assertFalse(self.contact.is_seen)
        self.client.get(self.url)
        self.contact.refresh_from_db()
        self.assertTrue(self.contact.is_seen)
