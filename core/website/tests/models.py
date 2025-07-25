from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import Profile

from ..models import ContactModel, JobTitle, NewsLetter, TeamMembers

User = get_user_model()


class TestContact(TestCase):
    def test_contact_creations(self):
        contact = ContactModel.objects.create(
            full_name="John Doe",
            email="johndoe@example.com",
            phone_number="09123456789",
            subject="Test Contact",
            content="This is a test message.",
        )
        self.assertEqual(contact.full_name, "John Doe")
        self.assertEqual(contact.email, "johndoe@example.com")
        self.assertEqual(contact.phone_number, "09123456789")
        self.assertEqual(contact.subject, "Test Contact")
        self.assertEqual(contact.content, "This is a test message.")
        self.assertFalse(contact.is_seen)


class TestJobTitle(TestCase):
    def test_job_title_creation(self):
        title = JobTitle.objects.create(title="Software Engineer")
        self.assertEqual(title.title, "Software Engineer")


class TestTeamMembers(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(
            email="test_shop@example.com", password="TestShop123@"
        )
        cls.profile = Profile.objects.get(user=cls.superuser)
        cls.profile.first_name = "John"
        cls.profile.last_name = "Doe"
        cls.profile.save()
        cls.title = JobTitle.objects.create(title="Software Engineer")
        cls.member = TeamMembers.objects.create(
            profile=cls.profile, description="This is a test description."
        )
        cls.member.job_title.set([cls.title])

    def test_team_member_creation(self):
        self.assertEqual(self.member.profile, self.profile)
        self.assertEqual(self.member.job_title.all()[0], self.title)
        self.assertEqual(
            self.member.description, "This is a test description."
        )
        self.assertTrue(self.member.status)


class TestNewsletter(TestCase):
    def test_newsletter_creation(self):
        newsletter = NewsLetter.objects.create(email="johndoe@example.com")
        self.assertEqual(newsletter.email, "johndoe@example.com")
