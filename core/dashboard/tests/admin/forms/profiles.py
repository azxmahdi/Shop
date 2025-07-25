from django.test import TestCase

from dashboard.admin.forms import AdminChangePasswordForm, AdminProfileEditForm


class AdminChangePasswordFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.valid_data = {
            "old_password": "TestPassword123/",
            "new_password": "ChangedPassword123/",
            "confirm_password": "ChangedPassword123/",
        }
        cls.form = AdminChangePasswordForm(cls.valid_data)

    def test_change_password_form_with_valid_data(self):
        self.assertTrue(self.form.is_valid())

    def test_change_password_form_with_invalid_data(self):
        invalid_data = self.valid_data.copy()
        invalid_data["confirm_password"] = ""
        form = AdminChangePasswordForm(invalid_data)
        self.assertFalse(form.is_valid())

    def test_validator_new_password_filed(self):
        invalid_data = self.valid_data.copy()
        invalid_data["new_password"] = "ChPa12/"
        form = AdminChangePasswordForm(invalid_data)
        self.assertIn("حداقل ۸ کاراکتر لازم است.", form.errors["new_password"])

        invalid_data = self.valid_data.copy()
        invalid_data["new_password"] = "changepassword123/"
        form = AdminChangePasswordForm(invalid_data)
        self.assertIn(
            "حداقل یک حرف بزرگ انگلیسی نیاز است.", form.errors["new_password"]
        )

        invalid_data = self.valid_data.copy()
        invalid_data["new_password"] = "CHANGEPASSWORD123/"
        form = AdminChangePasswordForm(invalid_data)
        self.assertIn(
            "حداقل یک حرف کوچک انگلیسی نیاز است.", form.errors["new_password"]
        )

        invalid_data = self.valid_data.copy()
        invalid_data["new_password"] = "ChangePassword/"
        form = AdminChangePasswordForm(invalid_data)
        self.assertIn("حداقل یک عدد نیاز است.", form.errors["new_password"])

        invalid_data = self.valid_data.copy()
        invalid_data["new_password"] = "ChangePassword123"
        form = AdminChangePasswordForm(invalid_data)
        self.assertIn(
            "حداقل یک نماد خاص نیاز است.", form.errors["new_password"]
        )

    def test_new_password_and_confirm_password_is_same(self):
        invalid_data = self.valid_data.copy()
        invalid_data["new_password"] = "Password123/"
        form = AdminChangePasswordForm(invalid_data)
        self.assertIn(
            "رمز عبور جدید و تأییدیه آن مطابقت ندارند.", form.errors["__all__"]
        )
        self.assertFalse(form.is_valid())


class AdminProfileEditFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.valid_data = {
            "delete_image": False,
            "first_name": "Test First Name",
            "last_name": "Test last Name",
            "phone_number": "09999999999",
            "image": "image.jpg",
        }
        cls.form = AdminProfileEditForm(cls.valid_data)

    def test_profile_edit_form_with_valid_data(self):
        self.assertTrue(self.form.is_valid())

    def test_profile_edit_form_with_invalid_data(self):
        invalid_data = self.valid_data.copy()
        invalid_data["first_name"] = ""
        form = AdminChangePasswordForm(invalid_data)
        self.assertFalse(form.is_valid())
