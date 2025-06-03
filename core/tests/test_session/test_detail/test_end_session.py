from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from core.tests.abstract_test_cases import AbstractStudySessionDetailTestCase
from core.models import StudySession


class EndStudySessionTestCase(AbstractStudySessionDetailTestCase):
    def test_end_active_session(self):
        """Должен позволять завершать активную сессию обучения"""
        # Сначала создаем активную сессию (ended_at=None)
        active_session = self._create_study_session_for_user(
            self.user,
            self.deck,
            ended_at=None
        )

        url = self._generate_url_for_end_session(active_session)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self._assert_study_session_fields_in_container(response.data)

        # Проверяем, что сессия была завершена
        self.assertIsNotNone(response.data['ended_at'])

        # Проверяем, что сессия завершена в базе данных
        session = StudySession.objects.get(id=active_session.id)
        self.assertIsNotNone(session.ended_at)

    def test_end_already_ended_session(self):
        """Не должен позволять завершать уже завершенную сессию"""
        # Создаем завершенную сессию
        ended_session = self._create_study_session_for_user(
            self.user,
            self.deck,
            ended_at=timezone.now()
        )

        url = self._generate_url_for_end_session(ended_session)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_end_session_of_another_user(self):
        """Не должен позволять завершать сессию другого пользователя"""
        # Создаем сессию обучения для другого пользователя
        other_deck = self._create_deck_for_user(self.another_user)
        other_session = self._create_study_session_for_user(
            self.another_user,
            other_deck,
            ended_at=None
        )

        url = reverse('core:session-end-session', args=(other_session.id,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Проверяем, что сессия не была завершена
        other_session = StudySession.objects.get(id=other_session.id)
        self.assertIsNone(other_session.ended_at)

    def test_end_non_existing_session(self):
        """Должен возвращать 404 при попытке завершить несуществующую сессию"""
        from core.models import StudySession
        non_existing_id = StudySession.objects.last().id + 1
        url = reverse('core:session-end-session', args=(non_existing_id,))

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_end_session_unauthenticated(self):
        """Неавторизованный пользователь не должен иметь возможность завершать сессии"""
        # Создаем активную сессию
        active_session = self._create_study_session_for_user(
            self.user,
            self.deck,
            ended_at=None
        )

        self.client.force_authenticate(user=None)

        url = self._generate_url_for_end_session(active_session)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Проверяем, что сессия не была завершена
        session = StudySession.objects.get(id=active_session.id)
        self.assertIsNone(session.ended_at)
