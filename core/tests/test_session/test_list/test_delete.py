from rest_framework import status
from core.tests.abstract_test_cases import AbstractStudySessionListTestCase


class DeleteStudySessionListTestCase(AbstractStudySessionListTestCase):
    def test_delete_not_allowed(self):
        """DELETE не должен быть разрешен для списка сессий обучения"""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
