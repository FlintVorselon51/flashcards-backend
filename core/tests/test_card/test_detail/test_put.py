from rest_framework import status
from core.tests.abstract_test_cases import AbstractCardDetailTestCase


class PutCardDetailTestCase(AbstractCardDetailTestCase):
    def test_put_own_card(self):
        """Должен позволять обновлять свою карточку"""
        payload = self._form_card_payload()

        response = self.client.put(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._assert_card_fields_in_container(response.data)

        # Проверяем, что данные карточки обновлены
        self.assertEqual(response.data['front'], payload['front'])
        self.assertEqual(response.data['back'], payload['back'])

    def test_put_card_from_public_deck_of_another_user(self):
        """Не должен позволять обновлять карточку из публичной колоды другого пользователя"""
        # Создаем публичную колоду другого пользователя и карточку в ней
        public_deck = self._create_deck_for_user(self.another_user, is_public=True)
        public_card = self._create_card_for_deck(public_deck)

        url = self._generate_url_for_card(public_card)
        payload = self._form_card_payload(deck=public_deck)

        response = self.client.put(url, data=payload, format='json')
        # Должен вернуть ошибку, так как пользователь не владеет колодой
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_card_from_private_deck_of_another_user(self):
        """Не должен позволять обновлять карточку из приватной колоды другого пользователя"""
        # Создаем приватную колоду другого пользователя и карточку в ней
        private_deck = self._create_deck_for_user(self.another_user, is_public=False)
        private_card = self._create_card_for_deck(private_deck)

        url = self._generate_url_for_card(private_card)
        payload = self._form_card_payload(deck=private_deck)

        response = self.client.put(url, data=payload, format='json')
        # API должно вернуть 404 для карточек в приватных колодах других пользователей
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_card_to_different_deck(self):
        """Должен позволять перемещать карточку в другую свою колоду"""
        # Создаем еще одну колоду для этого пользователя
        second_deck = self._create_deck_for_user(self.user)

        payload = self._form_card_payload(deck=second_deck)

        response = self.client.put(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что карточка перемещена в новую колоду
        self.assertEqual(response.data['deck'], second_deck.id)

    def test_put_card_to_deck_of_another_user(self):
        """Не должен позволять перемещать карточку в колоду другого пользователя"""
        # Создаем колоду другого пользователя
        other_user_deck = self._create_deck_for_user(self.another_user)

        payload = self._form_card_payload(deck=other_user_deck)

        response = self.client.put(self.url, data=payload, format='json')
        # Должен вернуть ошибку, так как пользователь не владеет колодой
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_card_without_front(self):
        """Не должен позволять обновлять карточку без лицевой стороны"""
        payload = self._form_card_payload(excluded_fields=('front',))

        response = self.client.put(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_card_without_back(self):
        """Не должен позволять обновлять карточку без обратной стороны"""
        payload = self._form_card_payload(excluded_fields=('back',))

        response = self.client.put(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_card_without_deck(self):
        """Не должен позволять обновлять карточку без указания колоды"""
        payload = self._form_card_payload(excluded_fields=('deck',))

        response = self.client.put(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_non_existing_card(self):
        """Должен возвращать 404 при попытке обновить несуществующую карточку"""
        url = self._generate_url_for_non_existing_card()
        payload = self._form_card_payload()

        response = self.client.put(url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_card_unauthenticated(self):
        """Неавторизованный пользователь не должен иметь возможность обновлять карточки"""
        self.client.force_authenticate(user=None)

        payload = self._form_card_payload()

        response = self.client.put(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
