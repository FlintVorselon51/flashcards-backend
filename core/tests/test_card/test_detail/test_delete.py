# core/tests/test_card/test_detail/test_delete.py
from rest_framework import status
from core.tests.abstract_test_cases import AbstractCardDetailTestCase
from core.models import Card


class DeleteCardDetailTestCase(AbstractCardDetailTestCase):
    def test_delete_own_card(self):
        """Должен позволять удалять свою карточку"""
        card_id = self.card.id

        # Проверяем, что карточка существует перед удалением
        self.assertTrue(Card.objects.filter(id=card_id).exists())

        # Удаляем карточку
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Проверяем, что карточка удалена
        self.assertFalse(Card.objects.filter(id=card_id).exists())

    def test_delete_card_from_public_deck_of_another_user(self):
        """Не должен позволять удалять карточку из публичной колоды другого пользователя"""
        # Создаем публичную колоду другого пользователя и карточку в ней
        public_deck = self._create_deck_for_user(self.another_user, is_public=True)
        public_card = self._create_card_for_deck(public_deck)
        card_id = public_card.id

        url = self._generate_url_for_card(public_card)

        # Проверяем, что карточка существует перед удалением
        self.assertTrue(Card.objects.filter(id=card_id).exists())

        # Пытаемся удалить карточку
        response = self.client.delete(url)
        # Должен вернуть ошибку, так как пользователь не владеет колодой
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Проверяем, что карточка не была удалена
        self.assertTrue(Card.objects.filter(id=card_id).exists())

    def test_delete_card_from_private_deck_of_another_user(self):
        """Не должен позволять удалять карточку из приватной колоды другого пользователя"""
        # Создаем приватную колоду другого пользователя и карточку в ней
        private_deck = self._create_deck_for_user(self.another_user, is_public=False)
        private_card = self._create_card_for_deck(private_deck)
        card_id = private_card.id

        url = self._generate_url_for_card(private_card)

        # Проверяем, что карточка существует перед удалением
        self.assertTrue(Card.objects.filter(id=card_id).exists())

        # Пытаемся удалить карточку
        response = self.client.delete(url)
        # API должно вернуть 404 для карточек в приватных колодах других пользователей
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Проверяем, что карточка не была удалена
        self.assertTrue(Card.objects.filter(id=card_id).exists())

    def test_delete_non_existing_card(self):
        """Должен возвращать 404 при попытке удалить несуществующую карточку"""
        url = self._generate_url_for_non_existing_card()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_card_unauthenticated(self):
        """Неавторизованный пользователь не должен иметь возможность удалять карточки"""
        card_id = self.card.id
        self.client.force_authenticate(user=None)

        # Пытаемся удалить карточку
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Проверяем, что карточка не была удалена
        self.assertTrue(Card.objects.filter(id=card_id).exists())
