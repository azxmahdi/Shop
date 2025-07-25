from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserType
from website.models import NewsLetter

User = get_user_model()


class AdminNewsletterListViewTest(TestCase):
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
        cls.newsletter1 = NewsLetter.objects.create(email="test1@example.com")
        cls.newsletter2 = NewsLetter.objects.create(email="test2@example.com")
        cls.url = reverse("dashboard:admin:newsletter-list")

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
        self.assertContains(response, self.newsletter1.email)

    def test_search_functionality(self):
        self.client.force_login(self.admin)
        response = self.client.get(self.url + "?q=test1@example.com")
        self.assertContains(response, self.newsletter1.email)
        self.assertNotContains(response, self.newsletter2.email)


class AdminNewsletterDeleteViewTest(TestCase):
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
        cls.newsletter = NewsLetter.objects.create(email="test@example.com")
        cls.url = reverse(
            "dashboard:admin:newsletter-delete", args=[cls.newsletter.pk]
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

    def test_delete(self):
        self.client.force_login(self.admin)
        response = self.client.post(self.url, follow=True)
        self.assertContains(response, "عضو مورد نظر با موفقیت حذف شد")
        self.assertFalse(
            NewsLetter.objects.filter(email=self.newsletter.email).exists()
        )
