from typing import Any

from django.urls import reverse
from rest_framework import status
from faker import Faker

from tools.test import AuthenticatedAPITestCase


fake = Faker()

Payload = dict[str, Any]


# noinspection DuplicatedCode
class SetNewPasswordUsingCurrentTestCase(AuthenticatedAPITestCase):
    url = reverse('auth:set-new-password-using-current')

    @staticmethod
    def _form_payload(current_password, new_password) -> Payload:
        return {
            'currentPassword': current_password,
            'newPassword': new_password
        }

    def test(self):
        new_password = fake.unique.password()

        self.assertEqual(self.user.check_password(self.password_for_user), True)
        self.assertEqual(self.user.check_password(new_password), False)

        payload = self._form_payload(self.password_for_user, new_password)
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(self.user.check_password(self.password_for_user), False)
        self.assertEqual(self.user.check_password(new_password), True)

    def test_wrong_current_password(self):
        wrong_password = fake.unique.password()
        new_password = fake.unique.password()

        payload = self._form_payload(wrong_password, new_password)
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_invalid_new_password(self):
        invalid_new_password = fake.unique.password(length=7)

        payload = self._form_payload(self.password_for_user, invalid_new_password)
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('errors', response.data)

    def test_no_current_password_provided(self):
        new_password = fake.unique.password()

        payload = self._form_payload(None, new_password)
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_no_new_password_provided(self):
        payload = self._form_payload(self.password_for_user, None)
        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

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
