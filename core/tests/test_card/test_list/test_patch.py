from rest_framework import status
from core.tests.abstract_test_cases import AbstractCardListTestCase


class PatchCardListTestCase(AbstractCardListTestCase):
    def test_patch_not_allowed(self):
        """PATCH не должен быть разрешен для списка карточек"""
        payload = {'front': 'New front'}

        response = self.client.patch(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
