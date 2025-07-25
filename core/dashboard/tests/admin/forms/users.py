from unittest.mock import MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import UserType
from dashboard.admin.forms import UserForm

User = get_user_model()


class AdminUserFormTest(TestCase):

    def _create_mock_request(self, is_superuser, type):
        mock_user = MagicMock()
        mock_user.is_superuser = is_superuser
        mock_user.type = type

        mock_request = MagicMock()
        mock_request.user = mock_user

        return mock_request

    def test_type_field_deleted_for_admin(self):
        request = self._create_mock_request(False, UserType.admin.value)
        user = User.objects.create_superuser(
            email="admin@gmail.com", password="Admin123/"
        )
        form = UserForm(request=request, instance=user)
        self.assertNotIn("type", form.fields)

    def test_type_field_deleted_for_customer(self):
        request = self._create_mock_request(True, UserType.customer.value)
        user = User.objects.create_superuser(
            email="customer@gmail.com", password="Customer123/"
        )
        form = UserForm(request=request, instance=user)
        self.assertNotIn("type", form.fields)

    def test_type_field_deleted_for_superuser_with_non_type_superuser(self):
        request = self._create_mock_request(True, UserType.admin.value)
        user = User.objects.create_superuser(
            email="admin@gmail.com", password="Admin123/"
        )
        form = UserForm(request=request, instance=user)
        self.assertNotIn("type", form.fields)

    def test_type_field_deleted_for_non_superuser_with_type_superuser(self):
        request = self._create_mock_request(True, UserType.admin.value)
        user = User.objects.create_superuser(
            email="admin@gmail.com", password="Admin123/"
        )
        form = UserForm(request=request, instance=user)
        self.assertNotIn("type", form.fields)

    def test_type_field_exists_for_actual_superuser(self):
        request = self._create_mock_request(True, UserType.superuser.value)
        user = User.objects.create_superuser(
            email="superuser@gmail.com", password="Superuser123/"
        )
        form = UserForm(request=request, instance=user)
        self.assertIn("type", form.fields)
        self.assertEqual(
            form.fields["type"].widget.attrs.get("class"), "form-select mb-3"
        )

    def test_submission_data_for_actual_superuser(self):
        request = self._create_mock_request(True, UserType.superuser.value)
        user = User.objects.create_superuser(
            email="superuser@gmail.com", password="Superuser123/"
        )
        data = {
            "email": "superuser@gmail.com",
            "type": UserType.superuser.value,
            "is_active": True,
            "is_verified": True,
        }
        form = UserForm(request=request, instance=user, data=data)
        self.assertTrue(form.is_valid())

    def test_submission_data_for_admin(self):
        request = self._create_mock_request(False, UserType.admin.value)
        user = User.objects.create_user(
            email="admin@gmail.com",
            password="Admin123/",
            type=UserType.admin.value,
        )
        data = {
            "email": "admin@gmail.com",
            "is_active": True,
            "is_verified": True,
        }
        form = UserForm(request=request, instance=user, data=data)
        self.assertTrue(form.is_valid())

    def test_submission_data_for_customer(self):
        request = self._create_mock_request(False, UserType.customer.value)
        user = User.objects.create_user(
            email="customer@gmail.com",
            password="Customer123/",
            type=UserType.customer.value,
        )
        data = {
            "email": "customer@gmail.com",
            "is_active": True,
            "is_verified": True,
        }
        form = UserForm(request=request, instance=user, data=data)
        self.assertTrue(form.is_valid())
