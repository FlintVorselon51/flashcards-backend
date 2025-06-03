from rest_framework import status
from core.tests.abstract_test_cases import AbstractStudySessionDetailTestCase


class PostStudySessionDetailTestCase(AbstractStudySessionDetailTestCase):
    def test_post_session(self):
        """PATCH должен быть запрещен для сессий обучения"""
        payload = {'deck': self.deck.id}

        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
