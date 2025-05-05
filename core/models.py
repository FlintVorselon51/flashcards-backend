from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# noinspection PyTypeChecker
class Deck(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decks')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Card(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='cards')
    front = models.TextField()
    back = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# noinspection PyTypeChecker
class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='study_sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)


# noinspection PyTypeChecker
class CardStudyData(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Again'),
        (2, 'Hard'),
        (3, 'Good'),
        (4, 'Easy'),
    ]

    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='study_data')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='card_study_data')
    ease_factor = models.FloatField(default=2.5)
    interval = models.IntegerField(default=0)
    last_reviewed = models.DateTimeField(null=True, blank=True)
    next_review = models.DateTimeField(null=True, blank=True)
    total_reviews = models.IntegerField(default=0)

    class Meta:
        unique_together = ('card', 'user')
