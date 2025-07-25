from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models import CustomUser, Profile, UserType


class TestUserType(TestCase):
    def test_choices_structure(self):
        expected_choices = [(1, "کاربر"), (2, "ادمین"), (3, "سوپر وایزر")]
        self.assertEqual(expected_choices, UserType.choices)


class CustomUserTest(TestCase):

    def test_create_user(self):
        user = CustomUser.objects.create_user(
            email="test@example.com", password="Test123@"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.type, UserType.customer.value)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_verified)

    def test_create_superuser(self):
        superuser = CustomUser.objects.create_superuser(
            email="superuser@example.com", password="Superuser123@"
        )
        self.assertEqual(superuser.type, UserType.superuser.value)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_verified)


class ProfileModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            email="user@example.com", password="User123@"
        )

    def test_profile_creation_via_signal(self):
        self.assertTrue(hasattr(self.user, "user_profile"))
        profile = self.user.user_profile
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.image, "profile/default.png")

    def test_profile_unique_constraint(self):
        self.assertTrue(hasattr(self.user, "user_profile"))

        with self.assertRaises(ValidationError):
            duplicate_profile = Profile(user=self.user)
            duplicate_profile.full_clean()
            duplicate_profile.save()

    def test_full_name_method(self):
        profile = self.user.user_profile
        profile.first_name = "John"
        profile.last_name = "Doe"
        profile.save()
        self.assertEqual(profile.full_name(), "John Doe")

    def test_get_fullname_method(self):
        profile = self.user.user_profile
        profile.first_name = "John"
        profile.last_name = "Doe"
        profile.save()
        self.assertEqual(profile.get_fullname(), "John Doe")
        profile.first_name = ""
        profile.last_name = ""
        profile.save()
        self.assertEqual(profile.get_fullname(), "کاربر جدید")

    def test_phone_number_validation(self):
        profile = self.user.user_profile
        profile.phone_number = "09130000000"
        profile.save()
        with self.assertRaises(ValidationError):
            profile.phone_number = "0912345678a"
            profile.full_clean()
            profile.save()
