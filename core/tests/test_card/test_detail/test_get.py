from rest_framework import status
from core.tests.abstract_test_cases import AbstractCardDetailTestCase


class GetCardDetailTestCase(AbstractCardDetailTestCase):
    def test_get_own_card(self):
        """Должен позволять получать информацию о своей карточке"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._assert_card_fields_in_container(response.data)

    def test_get_card_from_public_deck_of_another_user(self):
        """Должен позволять получать информацию о карточке из публичной колоды другого пользователя"""
        # Создаем публичную колоду другого пользователя и карточку в ней
        public_deck = self._create_deck_for_user(self.another_user, is_public=True)
        public_card = self._create_card_for_deck(public_deck)

        url = self._generate_url_for_card(public_card)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._assert_card_fields_in_container(response.data)

    def test_get_card_from_private_deck_of_another_user(self):
        """Не должен позволять получать информацию о карточке из приватной колоды другого пользователя"""
        # Создаем приватную колоду другого пользователя и карточку в ней
        private_deck = self._create_deck_for_user(self.another_user, is_public=False)
        private_card = self._create_card_for_deck(private_deck)

        url = self._generate_url_for_card(private_card)

        response = self.client.get(url)
        # API должно вернуть 404 для карточек в приватных колодах других пользователей
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_non_existing_card(self):
        """Должен возвращать 404 при попытке получить информацию о несуществующей карточке"""
        url = self._generate_url_for_non_existing_card()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_card_unauthenticated(self):
        """Неавторизованный пользователь не должен иметь доступ к API"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
