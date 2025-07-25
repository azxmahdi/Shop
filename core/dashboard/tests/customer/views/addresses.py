from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from order.models import UserAddressModel

User = get_user_model()


class CustomerAddressListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@gmail.com", password="User123/"
        )
        cls.address1 = UserAddressModel.objects.create(
            user=cls.user,
            address="My address 1",
            state="My state 1",
            city="My city 1",
            zip_code="1234",
        )
        cls.address2 = UserAddressModel.objects.create(
            user=cls.user,
            address="My address 2",
            state="My state 2",
            city="My city 2",
            zip_code="4321",
        )
        cls.url = reverse("dashboard:customer:address-list")

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_customer_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.address1.address)


class CustomerAddressCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@gmail.com", password="User123/"
        )
        cls.url = reverse("dashboard:customer:address-create")

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_customer_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_creation(self):
        self.client.force_login(self.user)
        data = {
            "address": "My address",
            "state": "My state",
            "city": "My city",
            "zip_code": "1234",
        }
        response = self.client.post(path=self.url, data=data, follow=True)
        self.assertContains(response, "ایجاد آدرس با موفقیت انجام شد")
        self.assertEqual(
            UserAddressModel.objects.filter(user=self.user).count(), 1
        )


class CustomerAddressEditViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@gmail.com", password="User123/"
        )
        cls.address = UserAddressModel.objects.create(
            user=cls.user,
            address="My address",
            state="My state",
            city="My city",
            zip_code="1234",
        )
        cls.url = reverse(
            "dashboard:customer:address-edit", kwargs={"pk": cls.address.pk}
        )

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_customer_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.address.address)

    def test_edition(self):
        self.client.force_login(self.user)
        data = {
            "address": "My address Updated",
            "state": "My state Updated",
            "city": "My city Updated",
            "zip_code": "1234 Updated",
        }
        response = self.client.post(path=self.url, data=data, follow=True)
        self.address.refresh_from_db()
        self.assertEqual(self.address.address, "My address Updated")
        self.assertEqual(self.address.state, "My state Updated")
        self.assertEqual(self.address.city, "My city Updated")
        self.assertEqual(self.address.zip_code, "1234 Updated")
        self.assertContains(response, "ویرایش آدرس با موفقیت انجام شد")


class CustomerAddressDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="user@gmail.com", password="User123/"
        )
        cls.address = UserAddressModel.objects.create(
            user=cls.user,
            address="My address",
            state="My state",
            city="My city",
            zip_code="1234",
        )
        cls.url = reverse(
            "dashboard:customer:address-delete", kwargs={"pk": cls.address.pk}
        )

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_customer_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.address.address)

    def test_deletion(self):
        self.client.force_login(self.user)
        response = self.client.post(path=self.url, follow=True)
        self.assertEqual(
            UserAddressModel.objects.filter(user=self.user).count(), 0
        )
