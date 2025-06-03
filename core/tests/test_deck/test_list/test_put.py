from rest_framework import status

from core.tests.abstract_test_cases import AbstractDeckListTestCase


class PutDeckListTestCase(AbstractDeckListTestCase):
    def test_put_not_allowed(self):
        response = self.client.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
