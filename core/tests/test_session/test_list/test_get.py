from rest_framework import status
from core.tests.abstract_test_cases import AbstractStudySessionListTestCase


class GetStudySessionListTestCase(AbstractStudySessionListTestCase):
    def test_get_sessions(self):
        """Должен возвращать список сессий обучения пользователя"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что сессия, созданная в setUp, есть в ответе
        self.assertTrue(len(response.data) >= 1)
        self._assert_study_session_fields_in_container(response.data[0])

    def test_get_sessions_excludes_sessions_of_others(self):
        """Не должен включать сессии обучения других пользователей"""
        # Создаем сессию обучения для другого пользователя
        other_deck = self._create_deck_for_user(self.another_user)
        other_session = self._create_study_session_for_user(self.another_user, other_deck)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что сессия другого пользователя не включена
        session_ids = [s['id'] for s in response.data]
        self.assertNotIn(other_session.id, session_ids)

    def test_get_sessions_unauthenticated(self):
        """Неавторизованный пользователь не должен иметь доступ к API"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
