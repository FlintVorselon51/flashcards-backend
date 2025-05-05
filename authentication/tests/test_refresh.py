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
class RefreshTestCase(APITestCase):
    url = reverse('auth:refresh')

    def setUp(self) -> None:
        email = fake.unique.email()
        password = fake.unique.password()

        self.user_example = User.objects.create_user(
            email=email,
            password=password
        )

        self.access_token_example = AccessToken(user=self.user_example).key
        self.refresh_token_example = RefreshToken(user=self.user_example).key

    @staticmethod
    def _form_payload(access_token, refresh_token) -> Payload:
        return {
            'accessToken': access_token,
            'refreshToken': refresh_token
        }

    def test(self):
        payload = self._form_payload(self.access_token_example, self.refresh_token_example)
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        access_token = AccessToken(key=response.data.get('accessToken'))
        refresh_token = RefreshToken(key=response.data.get('refreshToken'))

        user_from_access_token = access_token.get_user_from_token()
        user_from_refresh_token = refresh_token.get_user_from_token()

        self.assertEqual(user_from_access_token, self.user_example)
        self.assertEqual(user_from_refresh_token, self.user_example)

    def test_tokens_are_for_different_users(self):
        email = fake.unique.email()
        password = fake.unique.password()

        another_user = User.objects.create_user(
            email=email,
            password=password
        )

        access_token = AccessToken(user=another_user).key

        payload = self._form_payload(access_token, self.refresh_token_example)
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data.get('detail'), 'Provided tokens are invalid.')

    def test_invalid_access_token(self):
        invalid_access_token = fake.unique.pystr()

        payload = self._form_payload(invalid_access_token, self.refresh_token_example)
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data.get('detail'), 'Provided accessToken is invalid.')

    def test_invalid_refresh_token(self):
        invalid_refresh_token = fake.unique.pystr()

        payload = self._form_payload(self.access_token_example, invalid_refresh_token)
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data.get('detail'), 'Provided refreshToken is invalid.')

    def test_no_access_token_provided(self):
        payload = self._form_payload(None, self.refresh_token_example)
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data.get('detail'),
                         'Invalid request: accessToken and refreshToken fields are required.')

    def test_no_refresh_token_provided(self):
        payload = self._form_payload(self.access_token_example, None)
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data.get('detail'),
                         'Invalid request: accessToken and refreshToken fields are required.')

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
