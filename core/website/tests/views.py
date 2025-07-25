from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from website.models import ContactModel, JobTitle, NewsLetter, TeamMembers

User = get_user_model()


class IndexViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@gmail.com", password="User123/"
        )
        cls.url = reverse("website:index")

    def test_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class AboutViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(
            email="user@gmail.com", password="User123/"
        )
        cls.superuser.user_profile.first_name = "Test first name"
        cls.superuser.user_profile.last_name = "Test last name"
        cls.superuser.user_profile.save()

        job_title = JobTitle.objects.create(title="Job title")

        cls.team_member = TeamMembers.objects.create(
            profile=cls.superuser.user_profile,
            description="This is a test description",
            facebook_link="https://my_facebook.com",
            twitter_link="https://my_twitter.com",
            status=True,
        )

        cls.team_member.job_title.add(job_title)
        cls.url = reverse("website:about")

    def test_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.team_member.twitter_link)

    def test_context_data(self):
        response = self.client.get(self.url)
        self.assertQuerysetEqual(
            response.context["members"],
            TeamMembers.objects.filter(status=True),
        )


class ContactViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.data = {
            "full_name": "Test full name",
            "email": "user@gmail.com",
            "phone_number": "+989999999999",
            "subject": "Test subject",
            "content": "Test content",
        }
        cls.url = reverse("website:contact")

    def test_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_contact_with_valid_data(self):
        response = self.client.post(path=self.url, data=self.data, follow=True)
        self.assertContains(
            response, "همکاران ما به زودی با شما تماس خواهند گرفت"
        )
        self.assertEqual(ContactModel.objects.first().email, "user@gmail.com")

    def test_contact_with_invalid_data(self):
        data = self.data.copy()
        data["subject"] = ""
        response = self.client.post(path=self.url, data=data, follow=True)
        self.assertContains(response, "فرم معتبر نیست")
        self.assertFalse(ContactModel.objects.exists())


class NewsletterViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.data = {
            "email": "user@gmail.com",
        }
        cls.url = reverse("website:newsletter")

    def test_newsletter_with_valid_data(self):
        response = self.client.post(path=self.url, data=self.data, follow=True)
        self.assertContains(
            response,
            "از ثبت نام شما ممنونم، اخبار جدید رو براتون ارسال می کنم 😊👍",
        )
        self.assertEqual(NewsLetter.objects.first().email, "user@gmail.com")

    def test_newsletter_with_invalid_data(self):
        data = self.data.copy()
        data["email"] = ""
        response = self.client.post(path=self.url, data=data, follow=True)
        self.assertContains(
            response,
            "مشکلی در ارسال فرم شما وجود داشت که می دونم برا چی بود!! چون ربات هستید",
        )
        self.assertFalse(NewsLetter.objects.exists())
