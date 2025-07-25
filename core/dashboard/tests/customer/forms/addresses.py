from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import UserType
from dashboard.customer.forms import UserAddressForm
from order.models import UserAddressModel

User = get_user_model()


class CustomerUserAddressFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@gmail.com",
            password="User123/",
            type=UserType.customer.value,
        )
        cls.address = UserAddressModel.objects.create(
            user=cls.user,
            address="My address",
            state="My state",
            city="My city",
            zip_code="1234",
        )
        cls.valid_data = {
            "address": "My address",
            "state": "My state",
            "city": "My city",
            "zip_code": "1234",
        }

    def test_form_with_valid_data(self):
        form = UserAddressForm(instance=self.address, data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_form_with_invalid_data(self):
        invalid_data = self.valid_data.copy()
        invalid_data["city"] = ""
        form = UserAddressForm(instance=self.address, data=invalid_data)
        self.assertFalse(form.is_valid())
