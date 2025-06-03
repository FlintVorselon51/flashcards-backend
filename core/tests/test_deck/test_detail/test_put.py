from rest_framework import status
from core.tests.abstract_test_cases import AbstractDeckDetailTestCase


class PutDeckDetailTestCase(AbstractDeckDetailTestCase):
    def test_put_own_deck(self):
        payload = self._form_deck_payload_for_user(self.user)
        response = self.client.put(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._assert_deck_fields_in_container(response.data)

        # Проверяем, что имя колоды обновлено
        self.assertEqual(response.data['name'], payload['name'])

    def test_put_public_deck_of_another_user(self):
        # Создаем публичную колоду другого пользователя
        public_deck = self._create_deck_for_user(self.another_user, is_public=True)
        url = self._generate_url_for_deck(public_deck)

        payload = self._form_deck_payload_for_user(self.user)
        response = self.client.put(url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_without_name(self):
        payload = self._form_deck_payload_for_user(self.user, excluded_fields=('name',))
        response = self.client.put(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_non_existing_deck(self):
        url = self._generate_url_for_non_existing_deck()
        payload = self._form_deck_payload_for_user(self.user)
        response = self.client.put(url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_unauthenticated(self):
        self.client.force_authenticate(user=None)
        payload = self._form_deck_payload_for_user(self.user)
        response = self.client.put(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
