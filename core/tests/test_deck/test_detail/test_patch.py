from rest_framework import status
from core.tests.abstract_test_cases import AbstractDeckDetailTestCase


class PatchDeckDetailTestCase(AbstractDeckDetailTestCase):
    def test_patch_own_deck(self):
        payload = {'name': 'Updated Deck Name'}
        response = self.client.patch(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._assert_deck_fields_in_container(response.data)

        # Проверяем, что имя колоды обновлено
        self.assertEqual(response.data['name'], payload['name'])

    def test_patch_public_deck_of_another_user(self):
        # Создаем публичную колоду другого пользователя
        public_deck = self._create_deck_for_user(self.another_user, is_public=True)
        url = self._generate_url_for_deck(public_deck)

        payload = {'name': 'Updated Deck Name'}
        response = self.client.patch(url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_non_existing_deck(self):
        url = self._generate_url_for_non_existing_deck()
        payload = {'name': 'Updated Deck Name'}
        response = self.client.patch(url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_is_public_field(self):
        # Изменяем статус публичности колоды
        original_status = self.deck.is_public
        payload = {'is_public': not original_status}

        response = self.client.patch(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['is_public'], not original_status)

    def test_patch_unauthenticated(self):
        self.client.force_authenticate(user=None)
        payload = {'name': 'Updated Deck Name'}
        response = self.client.patch(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
