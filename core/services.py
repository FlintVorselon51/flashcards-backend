from datetime import datetime, timedelta

from django.db import models
from django.utils import timezone
from .models import CardStudyData, Card, Deck


class SpacedRepetitionService:
    @staticmethod
    def update_card_study_data(user, card_id, difficulty):
        try:
            card = Card.objects.get(id=card_id)
            if card.deck.owner != user and not card.deck.is_public:
                return None

            card_data, created = CardStudyData.objects.get_or_create(
                user=user,
                card=card
            )

            quality = (int(difficulty) - 1) * 5 / 3

            if not created:
                card_data.ease_factor = max(1.3, card_data.ease_factor + (
                            0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

            if quality < 3:
                card_data.interval = 1
            elif created or card_data.interval == 0:
                card_data.interval = 1
            elif card_data.interval == 1:
                card_data.interval = 6
            else:
                card_data.interval = int(card_data.interval * card_data.ease_factor)

            card_data.last_reviewed = timezone.now()
            card_data.next_review = timezone.now() + timedelta(days=card_data.interval)
            card_data.total_reviews += 1
            card_data.save()

            return card_data

        except Card.DoesNotExist:
            return None

    @staticmethod
    def get_due_cards(user, deck_id):
        """
        Retrieve cards due for review for a specific user and deck
        """
        now = timezone.now()

        try:
            deck = Deck.objects.filter(
                models.Q(owner=user) | models.Q(is_public=True),
                id=deck_id
            ).first()

            if not deck:
                return []

            all_cards_in_deck = deck.cards.all()

            due_cards_with_data = Card.objects.filter(
                deck_id=deck_id,
                study_data__user=user,
                study_data__next_review__lte=now
            )

            studied_card_ids = CardStudyData.objects.filter(
                user=user,
                card__deck_id=deck_id
            ).values_list('card_id', flat=True)

            new_cards = all_cards_in_deck.exclude(id__in=studied_card_ids)

            return list(due_cards_with_data) + list(new_cards)

        except Deck.DoesNotExist:
            return []
