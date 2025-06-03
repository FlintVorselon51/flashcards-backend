from rest_framework import status
from core.tests.abstract_test_cases import AbstractCardListTestCase
from core.tests.factories import DeckFactory, CardFactory


class GetCardListTestCase(AbstractCardListTestCase):
    def test_get_cards(self):
        """Должен возвращать список карточек пользователя"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что карточка, созданная в setUp, есть в ответе
        self.assertTrue(len(response.data) >= 1)
        self._assert_card_fields_in_container(response.data[0])

    def test_get_cards_includes_cards_from_public_decks(self):
        """Должен включать карточки из публичных колод других пользователей"""
        # Создаем публичную колоду другого пользователя и карточку в ней
        public_deck = self._create_deck_for_user(self.another_user, is_public=True)
        public_card = self._create_card_for_deck(public_deck)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что карточка из публичной колоды другого пользователя включена
        card_ids = [c['id'] for c in response.data]
        self.assertIn(public_card.id, card_ids)

    def test_get_cards_excludes_cards_from_private_decks_of_others(self):
        """Не должен включать карточки из приватных колод других пользователей"""
        # Создаем приватную колоду другого пользователя и карточку в ней
        private_deck = self._create_deck_for_user(self.another_user, is_public=False)
        private_card = self._create_card_for_deck(private_deck)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что карточка из приватной колоды другого пользователя не включена
        card_ids = [c['id'] for c in response.data]
        self.assertNotIn(private_card.id, card_ids)

    def test_get_cards_unauthenticated(self):
        """Неавторизованный пользователь не должен иметь доступ к API"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
