from django.urls import reverse
from rest_framework import status
from core.tests.abstract_test_cases import AbstractStudySessionDetailTestCase
from core.models import StudySession


class DeleteStudySessionDetailTestCase(AbstractStudySessionDetailTestCase):
    def test_delete_own_session(self):
        """Должен позволять удалять свою сессию обучения"""
        session_id = self.session.id

        # Проверяем, что сессия существует перед удалением
        self.assertTrue(StudySession.objects.filter(id=session_id).exists())

        # Удаляем сессию
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Проверяем, что сессия удалена
        self.assertFalse(StudySession.objects.filter(id=session_id).exists())

    def test_delete_session_of_another_user(self):
        """Не должен позволять удалять сессию обучения другого пользователя"""
        # Создаем сессию обучения для другого пользователя
        other_deck = self._create_deck_for_user(self.another_user)
        other_session = self._create_study_session_for_user(self.another_user, other_deck)
        session_id = other_session.id

        url = self._generate_url_for_session(other_session)

        # Проверяем, что сессия существует перед удалением
        self.assertTrue(StudySession.objects.filter(id=session_id).exists())

        # Пытаемся удалить сессию
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Проверяем, что сессия не была удалена
        self.assertTrue(StudySession.objects.filter(id=session_id).exists())

    def test_delete_non_existing_session(self):
        """Должен возвращать 404 при попытке удалить несуществующую сессию"""
        from core.models import StudySession
        non_existing_id = StudySession.objects.last().id + 1
        url = reverse('core:session-detail', args=(non_existing_id,))

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_session_unauthenticated(self):
        """Неавторизованный пользователь не должен иметь возможность удалять сессии"""
        session_id = self.session.id
        self.client.force_authenticate(user=None)

        # Пытаемся удалить сессию
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Проверяем, что сессия не была удалена
        self.assertTrue(StudySession.objects.filter(id=session_id).exists())
