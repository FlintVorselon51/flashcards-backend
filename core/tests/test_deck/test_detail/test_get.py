from rest_framework import status
from core.tests.abstract_test_cases import AbstractDeckDetailTestCase


class GetDeckDetailTestCase(AbstractDeckDetailTestCase):
    def test_get_own_deck(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._assert_deck_fields_in_container(response.data)
        self.assertIn('cards', response.data)  # DeckDetailSerializer включает карточки

    def test_get_public_deck_of_another_user(self):
        # Создаем публичную колоду другого пользователя
        public_deck = self._create_deck_for_user(self.another_user, is_public=True)
        url = self._generate_url_for_deck(public_deck)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._assert_deck_fields_in_container(response.data)

    def test_get_private_deck_of_another_user(self):
        # Создаем приватную колоду другого пользователя
        private_deck = self._create_deck_for_user(self.another_user, is_public=False)
        url = self._generate_url_for_deck(private_deck)

        response = self.client.get(url)
        # API возвращает 404 для приватных колод, которыми пользователь не владеет
        # чтобы не раскрывать существование колоды
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_non_existing_deck(self):
        url = self._generate_url_for_non_existing_deck()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
