# core/tests/abstract_test_cases.py
from abc import ABC
from typing import Any, Iterable
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from core.models import Deck, Card, StudySession, CardStudyData
from core.tests.factories import DeckFactory, CardFactory, StudySessionFactory, CardStudyDataFactory, UserFactory

User = get_user_model()

class AuthenticatedAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.another_user = UserFactory()
        self.client.force_authenticate(self.user)


class AbstractCoreTestCase(AuthenticatedAPITestCase, ABC):
    def setUp(self) -> None:
        super(AbstractCoreTestCase, self).setUp()
        self.deck = DeckFactory(owner=self.user)
        self.card = CardFactory(deck=self.deck)

    def _assert_deck_fields_in_container(self, container) -> None:
        self.assertIn('id', container)
        self.assertIn('name', container)
        self.assertIn('description', container)
        self.assertIn('owner', container)
        self.assertIn('owner_email', container)
        self.assertIn('is_public', container)
        self.assertIn('created_at', container)
        self.assertIn('updated_at', container)
        self.assertIn('cards_count', container)

    def _assert_card_fields_in_container(self, container) -> None:
        self.assertIn('id', container)
        self.assertIn('front', container)
        self.assertIn('back', container)
        self.assertIn('created_at', container)
        self.assertIn('updated_at', container)

    def _assert_study_session_fields_in_container(self, container) -> None:
        self.assertIn('id', container)
        self.assertIn('deck', container)
        self.assertIn('started_at', container)
        self.assertIn('ended_at', container)

    def _form_deck_payload_for_user(
            self,
            user,
            excluded_fields: Iterable[str] | None = None,
            **kwargs
    ) -> dict[str, Any]:
        if excluded_fields is None:
            excluded_fields = tuple()

        instance = DeckFactory.build(owner=user, **kwargs)

        payload = {
            'name': instance.name,
            'description': instance.description,
            'is_public': instance.is_public,
        }

        for excluded_field in excluded_fields:
            payload.pop(excluded_field)

        return payload

    def _form_card_payload(
            self,
            deck=None,
            excluded_fields: Iterable[str] | None = None,
            **kwargs
    ) -> dict[str, Any]:
        if excluded_fields is None:
            excluded_fields = tuple()

        if deck is None:
            deck = self.deck

        instance = CardFactory.build(deck=deck, **kwargs)

        payload = {
            'front': instance.front,
            'back': instance.back,
            'deck': deck.id,
        }

        for excluded_field in excluded_fields:
            payload.pop(excluded_field)

        return payload

    def _form_session_payload(
            self,
            deck=None,
            excluded_fields: Iterable[str] | None = None,
            **kwargs
    ) -> dict[str, Any]:
        if excluded_fields is None:
            excluded_fields = tuple()

        if deck is None:
            deck = self.deck

        payload = {
            'deck': deck.id,
        }

        for excluded_field in excluded_fields:
            payload.pop(excluded_field)

        return payload

    def _form_review_payload(
            self,
            card=None,
            difficulty=3,
            excluded_fields: Iterable[str] | None = None,
    ) -> dict[str, Any]:
        if excluded_fields is None:
            excluded_fields = tuple()

        if card is None:
            card = self.card

        payload = {
            'card_id': card.id,
            'difficulty': difficulty,
        }

        for excluded_field in excluded_fields:
            payload.pop(excluded_field)

        return payload

    @staticmethod
    def _create_deck_for_user(user, **kwargs) -> Deck:
        return DeckFactory(owner=user, **kwargs)

    @staticmethod
    def _create_card_for_deck(deck, **kwargs) -> Card:
        return CardFactory(deck=deck, **kwargs)

    @staticmethod
    def _create_study_session_for_user(user, deck, **kwargs) -> StudySession:
        return StudySessionFactory(user=user, deck=deck, **kwargs)

    @staticmethod
    def _create_card_study_data_for_user(user, card, **kwargs) -> CardStudyData:
        return CardStudyDataFactory(user=user, card=card, **kwargs)

    @staticmethod
    def _get_id_of_non_existing_deck() -> int:
        return Deck.objects.count() + 1

    @staticmethod
    def _get_id_of_non_existing_card() -> int:
        return Card.objects.count() + 1


class AbstractDeckListTestCase(AbstractCoreTestCase, ABC):
    def setUp(self) -> None:
        super(AbstractDeckListTestCase, self).setUp()
        # Используем правильное имя маршрута с пространством имен приложения
        self.url = reverse('core:deck-list')


class AbstractDeckDetailTestCase(AbstractCoreTestCase, ABC):
    def setUp(self) -> None:
        super(AbstractDeckDetailTestCase, self).setUp()
        self.url = reverse('core:deck-detail', args=(self.deck.id,))

    @staticmethod
    def _generate_url_for_deck(deck: Deck) -> str:
        return reverse('core:deck-detail', args=(deck.id,))

    @staticmethod
    def _generate_url_for_non_existing_deck() -> str:
        non_existing_deck_id = Deck.objects.last().id + 1
        url = reverse('core:deck-detail', args=(non_existing_deck_id,))
        return url


class AbstractCardListTestCase(AbstractCoreTestCase, ABC):
    def setUp(self) -> None:
        super(AbstractCardListTestCase, self).setUp()
        self.url = reverse('core:card-list')


class AbstractCardDetailTestCase(AbstractCoreTestCase, ABC):
    def setUp(self) -> None:
        super(AbstractCardDetailTestCase, self).setUp()
        self.url = reverse('core:card-detail', args=(self.card.id,))

    @staticmethod
    def _generate_url_for_card(card: Card) -> str:
        return reverse('core:card-detail', args=(card.id,))

    @staticmethod
    def _generate_url_for_non_existing_card() -> str:
        non_existing_card_id = Card.objects.last().id + 1
        url = reverse('core:card-detail', args=(non_existing_card_id,))
        return url


class AbstractStudySessionListTestCase(AbstractCoreTestCase, ABC):
    def setUp(self) -> None:
        super(AbstractStudySessionListTestCase, self).setUp()
        self.url = reverse('core:session-list')
        self.session = StudySessionFactory(user=self.user, deck=self.deck)


class AbstractStudySessionDetailTestCase(AbstractCoreTestCase, ABC):
    def setUp(self) -> None:
        super(AbstractStudySessionDetailTestCase, self).setUp()
        self.session = StudySessionFactory(user=self.user, deck=self.deck)
        self.url = reverse('core:session-detail', args=(self.session.id,))

    @staticmethod
    def _generate_url_for_session(session: StudySession) -> str:
        return reverse('core:session-detail', args=(session.id,))

    @staticmethod
    def _generate_url_for_end_session(session: StudySession) -> str:
        return reverse('core:session-end-session', args=(session.id,))


class AbstractReviewCardTestCase(AbstractCoreTestCase, ABC):
    def setUp(self) -> None:
        super(AbstractReviewCardTestCase, self).setUp()
        self.url = reverse('core:review')
