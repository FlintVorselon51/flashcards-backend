# core/tests/test_card/test_list/test_post.py
from rest_framework import status
from core.tests.abstract_test_cases import AbstractCardListTestCase
from core.models import Card


class PostCardListTestCase(AbstractCardListTestCase):
    def test_post_card(self):
        """Должен позволять создавать карточку в своей колоде"""
        payload = self._form_card_payload()

        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self._assert_card_fields_in_container(response.data)

        # Проверяем, что карточка создана с правильной колодой
        self.assertEqual(response.data['deck'], self.deck.id)

    def test_post_card_to_public_deck_of_another_user(self):
        """Не должен позволять создавать карточку в публичной колоде другого пользователя"""
        # Создаем публичную колоду другого пользователя
        public_deck = self._create_deck_for_user(self.another_user, is_public=True)

        payload = self._form_card_payload(deck=public_deck)

        response = self.client.post(self.url, data=payload, format='json')
        # Должен вернуть ошибку, так как пользователь не владеет колодой
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_card_to_private_deck_of_another_user(self):
        """Не должен позволять создавать карточку в приватной колоде другого пользователя"""
        # Создаем приватную колоду другого пользователя
        private_deck = self._create_deck_for_user(self.another_user, is_public=False)

        payload = self._form_card_payload(deck=private_deck)

        response = self.client.post(self.url, data=payload, format='json')
        # Должен вернуть ошибку, так как пользователь не владеет колодой
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_card_without_front(self):
        """Не должен позволять создавать карточку без лицевой стороны"""
        payload = self._form_card_payload(excluded_fields=('front',))

        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_card_without_back(self):
        """Не должен позволять создавать карточку без обратной стороны"""
        payload = self._form_card_payload(excluded_fields=('back',))

        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_card_without_deck(self):
        """Не должен позволять создавать карточку без указания колоды"""
        payload = self._form_card_payload(excluded_fields=('deck',))

        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_card_to_non_existing_deck(self):
        """Должен возвращать ошибку при попытке создать карточку в несуществующей колоде"""
        payload = self._form_card_payload()
        payload['deck'] = self._get_id_of_non_existing_deck()

        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_card_unauthenticated(self):
        """Неавторизованный пользователь не должен иметь возможность создавать карточки"""
        self.client.force_authenticate(user=None)

        payload = self._form_card_payload()

        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
