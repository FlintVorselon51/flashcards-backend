from typing import Any

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from faker import Faker

from tools.test import APITestCase


User = get_user_model()

fake = Faker()

Payload = dict[str, Any]


# noinspection DuplicatedCode
class RegistrationTestCase(APITestCase):
    url = reverse('auth:register')

    def setUp(self) -> None:
        self.email_example = fake.unique.email()
        self.password_example = fake.unique.password()

    @staticmethod
    def _form_payload(email, password) -> Payload:
        return {
            'email': email,
            'password': password
        }

    def test(self):
        payload = self._form_payload(self.email_example, self.password_example)
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(email=self.email_example)

        self.assertTrue(user.check_password(self.password_example))

    def test_email_already_exists(self):
        User.objects.create_user(
            email=self.email_example,
            password=self.password_example
        )

        payload = self._form_payload(self.email_example, self.password_example)
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data.get('detail'), 'Provided email already in use.')

    def test_invalid_email(self):
        invalid_email = fake.unique.pystr()

        payload = self._form_payload(invalid_email, self.password_example)
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('errors', response.data)
        self.assertEqual(response.data.get('message'), 'Provided email is invalid.')

    def test_invalid_password(self):
        invalid_password = fake.unique.password(length=7)

        payload = self._form_payload(self.email_example, invalid_password)
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('errors', response.data)
        self.assertEqual(response.data.get('message'), 'Provided password is invalid.')

    def test_no_email_provided(self):
        payload = self._form_payload(None, self.password_example)
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data.get('detail'), 'Invalid request: email and password fields are required.')

    def test_no_password_provided(self):
        payload = self._form_payload(self.email_example, None)
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data.get('detail'), 'Invalid request: email and password fields are required.')

    def test_get_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_not_allowed(self):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_not_allowed(self):
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_not_allowed(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
