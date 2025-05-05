from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from faker import Faker

from tools.test import APITestCase


User = get_user_model()

fake = Faker()


# noinspection DuplicatedCode
class IsEmailAvailableForRegistrationTestCase(APITestCase):
    url = reverse('auth:is-email-available-for-registration')

    def _form_url(self, email) -> None:
        self.url += f'?email={email}'

    def test_user_available(self):
        email = fake.unique.email()

        self._form_url(email)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(response.data.get('available'))
        self.assertEqual(response.data.get('email'), email)

    def test_user_not_available(self):
        email = fake.unique.email()
        password = fake.unique.password()

        User.objects.create_user(
            email=email,
            password=password
        )

        self._form_url(email)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(response.data.get('available'))
        self.assertEqual(response.data.get('email'), email)

    def test_empty_email(self):
        self._form_url('')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(response.data.get('detail'), 'Invalid request: email field is required.')

    def test_post_not_allowed(self):
        response = self.client.post(self.url)
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
