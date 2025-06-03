# core/tests/test_deck/test_detail/test_delete.py
from rest_framework import status
from core.tests.abstract_test_cases import AbstractDeckDetailTestCase
from core.models import Deck


class DeleteDeckDetailTestCase(AbstractDeckDetailTestCase):
    def test_delete_own_deck(self):
        """Владелец колоды должен иметь возможность удалить её"""
        deck_id = self.deck.id

        # Проверяем, что колода существует перед удалением
        self.assertTrue(Deck.objects.filter(id=deck_id).exists())

        # Удаляем колоду
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Проверяем, что колода удалена
        self.assertFalse(Deck.objects.filter(id=deck_id).exists())

    def test_delete_public_deck_of_another_user(self):
        """Пользователь не должен иметь возможность удалить чужую публичную колоду"""
        # Создаем публичную колоду другого пользователя
        public_deck = self._create_deck_for_user(self.another_user, is_public=True)
        deck_id = public_deck.id
        url = self._generate_url_for_deck(public_deck)

        # Проверяем, что колода существует перед удалением
        self.assertTrue(Deck.objects.filter(id=deck_id).exists())

        # Пытаемся удалить колоду
        response = self.client.delete(url)
        # API должно вернуть 403 (Forbidden) для попытки удаления чужой колоды
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Проверяем, что колода не была удалена
        self.assertTrue(Deck.objects.filter(id=deck_id).exists())

    def test_delete_private_deck_of_another_user(self):
        """Пользователь не должен иметь возможность удалить чужую приватную колоду"""
        # Создаем приватную колоду другого пользователя
        private_deck = self._create_deck_for_user(self.another_user, is_public=False)
        deck_id = private_deck.id
        url = self._generate_url_for_deck(private_deck)

        # Проверяем, что колода существует перед удалением
        self.assertTrue(Deck.objects.filter(id=deck_id).exists())

        # Пытаемся удалить колоду
        response = self.client.delete(url)

        # API должно вернуть 404 (Not Found) для чужой приватной колоды
        # это согласуется с логикой скрытия существования приватных колод
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Проверяем, что колода не была удалена
        self.assertTrue(Deck.objects.filter(id=deck_id).exists())

    def test_delete_non_existing_deck(self):
        """Попытка удаления несуществующей колоды должна возвращать 404"""
        url = self._generate_url_for_non_existing_deck()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_deck_cards_cascade(self):
        """При удалении колоды должны удаляться все её карточки"""
        # Создаем несколько карточек для колоды
        cards = [self._create_card_for_deck(self.deck) for _ in range(3)]
        card_ids = [card.id for card in cards]

        # Проверяем, что карточки существуют
        from core.models import Card
        self.assertEqual(Card.objects.filter(id__in=card_ids).count(), 3)

        # Удаляем колоду
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Проверяем, что карточки были удалены вместе с колодой
        self.assertEqual(Card.objects.filter(id__in=card_ids).count(), 0)

    def test_delete_deck_unauthenticated(self):
        """Неавторизованный пользователь не должен иметь возможность удалить колоду"""
        deck_id = self.deck.id
        self.client.force_authenticate(user=None)

        # Пытаемся удалить колоду
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Проверяем, что колода не была удалена
        self.assertTrue(Deck.objects.filter(id=deck_id).exists())

    def test_delete_deck_as_another_user(self):
        """Другой пользователь не должен иметь возможность удалить чужую колоду"""
        deck_id = self.deck.id
        self.client.force_authenticate(user=self.another_user)

        # Пытаемся удалить колоду
        response = self.client.delete(self.url)
        # API должно вернуть 403 (Forbidden) или 404 (Not Found)
        # в зависимости от того, является ли колода публичной или приватной
        expected_status = status.HTTP_403_FORBIDDEN if self.deck.is_public else status.HTTP_404_NOT_FOUND
        self.assertEqual(response.status_code, expected_status)

        # Проверяем, что колода не была удалена
        self.assertTrue(Deck.objects.filter(id=deck_id).exists())
