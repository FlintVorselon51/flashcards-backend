from rest_framework import status
from core.tests.abstract_test_cases import AbstractCardListTestCase


class DeleteCardListTestCase(AbstractCardListTestCase):
    def test_delete_not_allowed(self):
        """DELETE не должен быть разрешен для списка карточек"""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
