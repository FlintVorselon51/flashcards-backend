from rest_framework import status
from core.tests.abstract_test_cases import AbstractStudySessionListTestCase


class PutStudySessionListTestCase(AbstractStudySessionListTestCase):
    def test_put_not_allowed(self):
        """PUT не должен быть разрешен для списка сессий обучения"""
        payload = self._form_session_payload()

        response = self.client.put(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
