from rest_framework import status
from core.tests.abstract_test_cases import AbstractCardDetailTestCase


class PostCardListTestCase(AbstractCardDetailTestCase):
    def test_put_not_allowed(self):
        """PUT не должен быть разрешен для списка карточек"""
        payload = self._form_card_payload()

        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
