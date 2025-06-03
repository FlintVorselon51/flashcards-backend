from django.urls import reverse
from rest_framework import status
from core.tests.abstract_test_cases import AbstractStudySessionDetailTestCase


class GetStudySessionDetailTestCase(AbstractStudySessionDetailTestCase):
    def test_get_own_session(self):
        """Должен позволять получать информацию о своей сессии обучения"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._assert_study_session_fields_in_container(response.data)

    def test_get_session_of_another_user(self):
        """Не должен позволять получать информацию о сессии обучения другого пользователя"""
        # Создаем сессию обучения для другого пользователя
        other_deck = self._create_deck_for_user(self.another_user)
        other_session = self._create_study_session_for_user(self.another_user, other_deck)

        url = self._generate_url_for_session(other_session)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_non_existing_session(self):
        """Должен возвращать 404 при попытке получить информацию о несуществующей сессии"""
        from core.models import StudySession
        non_existing_id = StudySession.objects.last().id + 1
        url = reverse('core:session-detail', args=(non_existing_id,))

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_session_unauthenticated(self):
        """Неавторизованный пользователь не должен иметь доступ к API"""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
