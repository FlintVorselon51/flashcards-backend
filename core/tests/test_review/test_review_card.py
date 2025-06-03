from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from core.tests.abstract_test_cases import AbstractReviewCardTestCase
from core.models import CardStudyData, Card


class ReviewCardViewTestCase(AbstractReviewCardTestCase):
    def test_review_own_card(self):
        """Должен позволять отправлять отзыв о своей карточке"""
        payload = self._form_review_payload(difficulty=3)  # 'Good' difficulty

        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что создана запись CardStudyData
        self.assertTrue(CardStudyData.objects.filter(
            user=self.user,
            card=self.card
        ).exists())

        # Проверяем поля в ответе
        self.assertIn('id', response.data)
        self.assertIn('ease_factor', response.data)
        self.assertIn('interval', response.data)
        self.assertIn('last_reviewed', response.data)
        self.assertIn('next_review', response.data)
        self.assertIn('total_reviews', response.data)

    def test_review_card_from_public_deck_of_another_user(self):
        """Должен позволять отправлять отзыв о карточке из публичной колоды другого пользователя"""
        # Создаем публичную колоду другого пользователя и карточку в ней
        public_deck = self._create_deck_for_user(self.another_user, is_public=True)
        public_card = self._create_card_for_deck(public_deck)

        payload = self._form_review_payload(card=public_card, difficulty=3)

        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что создана запись CardStudyData
        self.assertTrue(CardStudyData.objects.filter(
            user=self.user,
            card=public_card
        ).exists())

    def test_review_card_from_private_deck_of_another_user(self):
        """Не должен позволять отправлять отзыв о карточке из приватной колоды другого пользователя"""
        # Создаем приватную колоду другого пользователя и карточку в ней
        private_deck = self._create_deck_for_user(self.another_user, is_public=False)
        private_card = self._create_card_for_deck(private_deck)

        payload = self._form_review_payload(card=private_card, difficulty=3)

        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Проверяем, что запись CardStudyData НЕ создана
        self.assertFalse(CardStudyData.objects.filter(
            user=self.user,
            card=private_card
        ).exists())

    def test_review_non_existing_card(self):
        """Должен возвращать 404 при попытке отправить отзыв о несуществующей карточке"""
        payload = {
            'card_id': self._get_id_of_non_existing_card(),
            'difficulty': 3
        }

        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_review_card_with_invalid_difficulty(self):
        """Должен возвращать ошибку при отправке отзыва с неверным значением difficulty"""
        # Значение 5 находится вне допустимого диапазона (1-4)
        payload = self._form_review_payload(difficulty=5)

        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_card_without_card_id(self):
        """Должен возвращать ошибку при отправке отзыва без указания card_id"""
        payload = self._form_review_payload(excluded_fields=('card_id',))

        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_card_without_difficulty(self):
        """Должен возвращать ошибку при отправке отзыва без указания difficulty"""
        payload = self._form_review_payload(excluded_fields=('difficulty',))

        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_card_unauthenticated(self):
        """Неавторизованный пользователь не должен иметь возможность отправлять отзывы"""
        self.client.force_authenticate(user=None)

        payload = self._form_review_payload()

        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Проверяем, что запись CardStudyData НЕ создана
        self.assertFalse(CardStudyData.objects.filter(
            user=self.user,
            card=self.card
        ).exists())

    def test_sm2_algorithm_different_difficulties(self):
        """Проверяем, что алгоритм SM-2 корректно рассчитывает интервалы для разных уровней сложности"""
        # Тестируем разные уровни сложности
        difficulties = [1, 2, 3, 4]  # Again, Hard, Good, Easy
        expected_intervals = []

        for difficulty in difficulties:
            # Удаляем предыдущие данные (если есть)
            CardStudyData.objects.filter(user=self.user, card=self.card).delete()

            payload = self._form_review_payload(difficulty=difficulty)
            response = self.client.post(self.url, data=payload, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            # Сохраняем интервал для этого уровня сложности
            study_data = CardStudyData.objects.get(user=self.user, card=self.card)
            expected_intervals.append(study_data.interval)

        # Проверяем, что интервалы увеличиваются с повышением легкости
        # Again (1) должен иметь самый маленький интервал, Easy (4) - самый большой
        self.assertTrue(
            expected_intervals[0] <= expected_intervals[1] <= expected_intervals[2] <= expected_intervals[3])

    def test_sm2_algorithm_repeated_reviews(self):
        """Проверяем, что при повторных отзывах интервалы увеличиваются согласно алгоритму SM-2"""
        # Первый отзыв - Good (3)
        payload = self._form_review_payload(difficulty=3)
        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        first_interval = CardStudyData.objects.get(user=self.user, card=self.card).interval

        # Обновляем дату последнего повторения, чтобы можно было отправить новый отзыв
        study_data = CardStudyData.objects.get(user=self.user, card=self.card)
        study_data.last_reviewed = timezone.now() - timedelta(days=study_data.interval)
        study_data.save()

        # Второй отзыв - тоже Good (3)
        response = self.client.post(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        second_interval = CardStudyData.objects.get(user=self.user, card=self.card).interval

        # Проверяем, что интервал увеличился
        self.assertTrue(second_interval > first_interval)

    def test_get_method_not_allowed(self):
        """GET не должен быть разрешен для ReviewCardView"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_method_not_allowed(self):
        """PUT не должен быть разрешен для ReviewCardView"""
        payload = self._form_review_payload()
        response = self.client.put(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_patch_method_not_allowed(self):
        """PATCH не должен быть разрешен для ReviewCardView"""
        payload = {'difficulty': 3}
        response = self.client.patch(self.url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_method_not_allowed(self):
        """DELETE не должен быть разрешен для ReviewCardView"""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
