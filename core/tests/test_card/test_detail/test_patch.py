from rest_framework import status
from core.tests.abstract_test_cases import AbstractCardDetailTestCase


class PatchCardDetailTestCase(AbstractCardDetailTestCase):
    def test_patch_own_card(self):
        """Должен позволять частично обновлять свою карточку"""
        payload = {'front': 'New front text'}

        response = self.client.patch(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._assert_card_fields_in_container(response.data)

        # Проверяем, что данные карточки обновлены
        self.assertEqual(response.data['front'], payload['front'])

    def test_patch_card_from_public_deck_of_another_user(self):
        """Не должен позволять обновлять карточку из публичной колоды другого пользователя"""
        # Создаем публичную колоду другого пользователя и карточку в ней
        public_deck = self._create_deck_for_user(self.another_user, is_public=True)
        public_card = self._create_card_for_deck(public_deck)

        url = self._generate_url_for_card(public_card)
        payload = {'front': 'New front text'}

        response = self.client.patch(url, data=payload, format='json')
        # Должен вернуть ошибку, так как пользователь не владеет колодой
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_card_to_different_deck(self):
        """Должен позволять перемещать карточку в другую свою колоду"""
        # Создаем еще одну колоду для этого пользователя
        second_deck = self._create_deck_for_user(self.user)

        payload = {'deck': second_deck.id}

        response = self.client.patch(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что карточка перемещена в новую колоду
        self.assertEqual(response.data['deck'], second_deck.id)

    def test_patch_non_existing_card(self):
        """Должен возвращать 404 при попытке обновить несуществующую карточку"""
        url = self._generate_url_for_non_existing_card()
        payload = {'front': 'New front text'}

        response = self.client.patch(url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_card_unauthenticated(self):
        """Неавторизованный пользователь не должен иметь возможность обновлять карточки"""
        self.client.force_authenticate(user=None)

        payload = {'front': 'New front text'}

        response = self.client.patch(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
