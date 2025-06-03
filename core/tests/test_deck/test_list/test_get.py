from rest_framework import status
from core.tests.abstract_test_cases import AbstractDeckListTestCase


class GetDeckListTestCase(AbstractDeckListTestCase):
    def test_get_deck_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Должен возвращать как минимум колоду, созданную в setUp
        self.assertTrue(len(response.data) >= 1)
        self._assert_deck_fields_in_container(response.data[0])

    def test_get_deck_list_includes_public_decks(self):
        # Создаем публичную колоду другого пользователя
        public_deck = self._create_deck_for_user(self.another_user, is_public=True)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        deck_ids = [d['id'] for d in response.data]
        self.assertIn(public_deck.id, deck_ids)

    def test_get_deck_list_excludes_private_decks_of_others(self):
        # Создаем приватную колоду другого пользователя
        private_deck = self._create_deck_for_user(self.another_user, is_public=False)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        deck_ids = [d['id'] for d in response.data]
        self.assertNotIn(private_deck.id, deck_ids)

    def test_get_deck_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
