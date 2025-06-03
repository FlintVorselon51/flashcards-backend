from rest_framework import status
from core.tests.abstract_test_cases import AbstractStudySessionDetailTestCase


class PutStudySessionDetailTestCase(AbstractStudySessionDetailTestCase):
    def test_put_session(self):
        """PUT должен быть запрещен для сессий обучения"""
        payload = self._form_session_payload()

        response = self.client.put(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
