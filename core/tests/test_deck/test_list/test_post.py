from rest_framework import status
from core.tests.abstract_test_cases import AbstractDeckListTestCase
from core.models import Deck


class PostDeckListTestCase(AbstractDeckListTestCase):
    def test_post_deck(self):
        payload = self._form_deck_payload_for_user(self.user)
        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self._assert_deck_fields_in_container(response.data)

        self.assertEqual(response.data['owner'], self.user.id)
        self.assertEqual(response.data['owner_email'], self.user.email)

    def test_post_deck_without_name(self):
        payload = self._form_deck_payload_for_user(self.user, excluded_fields=('name',))
        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_deck_unauthenticated(self):
        self.client.force_authenticate(user=None)
        payload = self._form_deck_payload_for_user(self.user)
        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
