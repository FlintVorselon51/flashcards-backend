from rest_framework import status
from core.tests.abstract_test_cases import AbstractStudySessionListTestCase
from core.models import StudySession


class PostStudySessionListTestCase(AbstractStudySessionListTestCase):
    def test_post_session(self):
        """Должен позволять создавать сессию обучения для своей колоды"""
        payload = self._form_session_payload()

        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self._assert_study_session_fields_in_container(response.data)

        # Проверяем, что сессия создана с правильной колодой и пользователем
        self.assertEqual(response.data['deck'], self.deck.id)

        # Проверяем, что сессия существует в базе данных
        self.assertTrue(StudySession.objects.filter(id=response.data['id']).exists())

    def test_post_session_for_public_deck_of_another_user(self):
        """Должен позволять создавать сессию обучения для публичной колоды другого пользователя"""
        # Создаем публичную колоду другого пользователя
        public_deck = self._create_deck_for_user(self.another_user, is_public=True)

        payload = self._form_session_payload(deck=public_deck)

        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем, что сессия создана с правильной колодой
        self.assertEqual(response.data['deck'], public_deck.id)

    def test_post_session_for_private_deck_of_another_user(self):
        """Не должен позволять создавать сессию обучения для приватной колоды другого пользователя"""
        # Создаем приватную колоду другого пользователя
        private_deck = self._create_deck_for_user(self.another_user, is_public=False)

        payload = self._form_session_payload(deck=private_deck)

        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_session_without_deck(self):
        """Не должен позволять создавать сессию обучения без указания колоды"""
        payload = self._form_session_payload(excluded_fields=('deck',))

        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_session_for_non_existing_deck(self):
        """Должен возвращать 404 при попытке создать сессию для несуществующей колоды"""
        payload = {'deck': self._get_id_of_non_existing_deck()}

        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_session_unauthenticated(self):
        """Неавторизованный пользователь не должен иметь возможность создавать сессии обучения"""
        self.client.force_authenticate(user=None)

        payload = self._form_session_payload()

        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
