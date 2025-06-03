# core/tests/test_deck/test_detail/test_start_session.py
from rest_framework import status
from django.urls import reverse
from core.tests.abstract_test_cases import AbstractDeckDetailTestCase
from core.models import StudySession


class StartSessionDeckDetailTestCase(AbstractDeckDetailTestCase):
    def test_start_session_for_own_deck(self):
        url = reverse('core:deck-start-session', args=(self.deck.id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self._assert_study_session_fields_in_container(response.data)

        # Проверяем, что сессия создана с правильными данными
        self.assertEqual(response.data['deck'], self.deck.id)

        # Проверяем, что сессия существует в базе данных
        self.assertTrue(StudySession.objects.filter(id=response.data['id']).exists())

    def test_start_session_for_public_deck_of_another_user(self):
        # Создаем публичную колоду другого пользователя
        public_deck = self._create_deck_for_user(self.another_user, is_public=True)

        url = reverse('core:deck-start-session', args=(public_deck.id,))
        response = self.client.post(url)
        # Нельзя создавать колоды другим пользователям
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_start_session_for_private_deck_of_another_user(self):
        # Создаем приватную колоду другого пользователя
        private_deck = self._create_deck_for_user(self.another_user, is_public=False)

        url = reverse('core:deck-start-session', args=(private_deck.id,))
        response = self.client.post(url)
        # API возвращает 404 для приватных колод других пользователей
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_start_session_for_non_existing_deck(self):
        url = reverse('core:deck-start-session', args=(self._get_id_of_non_existing_deck(),))
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_start_session_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse('core:deck-start-session', args=(self.deck.id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
