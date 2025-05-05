from typing import Any

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from faker import Faker

from tools.test import APITestCase
from authentication.services.tokens import AccessToken, RefreshToken


User = get_user_model()

fake = Faker()

Payload = dict[str, Any]


# noinspection DuplicatedCode
class LoginTestCase(APITestCase):
    url = reverse('auth:login')

    email_for_user = fake.unique.email()
    password_for_user = fake.unique.password()

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email=self.email_for_user,
            password=self.password_for_user
        )

    @staticmethod
    def _form_payload(email, password) -> Payload:
        return {
            'email': email,
            'password': password
        }

    def test(self):
        payload = self._form_payload(self.email_for_user, self.password_for_user)
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        access_token = AccessToken(key=response.data.get('accessToken'))
        refresh_token = RefreshToken(key=response.data.get('refreshToken'))

        user_from_access_token = access_token.get_user_from_token()
        user_from_refresh_token = refresh_token.get_user_from_token()

        self.assertEqual(user_from_access_token, self.user)
        self.assertEqual(user_from_refresh_token, self.user)

    def test_non_existing_user(self):
        email_for_non_existing_user = fake.unique.email()

        payload = self._form_payload(email_for_non_existing_user, self.password_for_user)
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data.get('detail'), 'User with provided email not found.')

    def test_wrong_password(self):
        wrong_password = fake.unique.password()

        payload = self._form_payload(self.email_for_user, wrong_password)
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data.get('detail'), 'Wrong password.')

    def test_no_email_provided(self):
        payload = self._form_payload(None, self.password_for_user)
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data.get('detail'), 'Invalid request: email and password fields are required.')

    def test_no_password_provided(self):
        payload = self._form_payload(self.email_for_user, None)
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
