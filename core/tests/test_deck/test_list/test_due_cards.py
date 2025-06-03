# core/tests/test_deck/test_detail/test_due_cards.py
from rest_framework import status
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta
from core.tests.abstract_test_cases import AbstractDeckDetailTestCase
from core.tests.factories import CardFactory, CardStudyDataFactory


class DueCardsDeckDetailTestCase(AbstractDeckDetailTestCase):
    def test_get_due_cards(self):
        # Создаем дополнительные карточки
        card1 = CardFactory(deck=self.deck)
        card2 = CardFactory(deck=self.deck)
        card3 = CardFactory(deck=self.deck)

        # Настраиваем карточку 1 как просроченную (due)
        CardStudyDataFactory(
            card=card1,
            user=self.user,
            next_review=timezone.now() - timedelta(days=1)
        )

        # Настраиваем карточку 2 как не просроченную (not due yet)
        CardStudyDataFactory(
            card=card2,
            user=self.user,
            next_review=timezone.now() + timedelta(days=1)
        )

        # Карточка 3 не имеет данных о изучении (новая карточка)

        url = reverse('core:deck-due-cards', args=(self.deck.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Мы ожидаем 3 карточки в результате: карточка созданная в setUp + card1 + card3
        expected_count = 3  # Соответствует реальному поведению API
        self.assertEqual(len(response.data), expected_count)

        card_ids = [c['id'] for c in response.data]
        self.assertIn(card1.id, card_ids)
        self.assertNotIn(card2.id, card_ids)
        self.assertIn(card3.id, card_ids)

    def test_get_due_cards_for_public_deck_of_another_user(self):
        # Создаем публичную колоду другого пользователя с карточками
        public_deck = self._create_deck_for_user(self.another_user, is_public=True)
        card = CardFactory(deck=public_deck)

        url = reverse('core:deck-due-cards', args=(public_deck.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Должна быть одна карточка (новая)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], card.id)

    def test_get_due_cards_for_private_deck_of_another_user(self):
        # Создаем приватную колоду другого пользователя
        private_deck = self._create_deck_for_user(self.another_user, is_public=False)

        url = reverse('core:deck-due-cards', args=(private_deck.id,))
        response = self.client.get(url)
        # API возвращает 404 для приватных колод других пользователей
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_due_cards_for_non_existing_deck(self):
        url = reverse('core:deck-due-cards', args=(self._get_id_of_non_existing_deck(),))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_due_cards_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse('core:deck-due-cards', args=(self.deck.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
