# core/tests/factories.py
import factory
from faker import Faker
from django.contrib.auth import get_user_model
from core.models import Deck, Card, StudySession, CardStudyData
from datetime import timedelta
from django.utils import timezone

fake = Faker()

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.LazyAttribute(lambda _: fake.unique.email())
    name = factory.LazyAttribute(lambda _: fake.name())
    password = factory.PostGenerationMethodCall('set_password', 'SecurePassword123')


class DeckFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Deck

    name = factory.LazyAttribute(lambda _: f"Deck {fake.word()}")
    description = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=200))
    owner = factory.SubFactory(UserFactory)
    is_public = factory.LazyAttribute(lambda _: fake.boolean(chance_of_getting_true=25))


class CardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Card

    deck = factory.SubFactory(DeckFactory)
    front = factory.LazyAttribute(lambda _: fake.sentence())
    back = factory.LazyAttribute(lambda _: fake.text(max_nb_chars=200))


class StudySessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StudySession

    user = factory.SubFactory(UserFactory)
    deck = factory.SubFactory(DeckFactory)
    started_at = factory.LazyFunction(lambda: timezone.now())
    ended_at = None  # По умолчанию создаем активные сессии
    # ended_at = factory.LazyAttribute(
    #     lambda obj: obj.started_at + timedelta(minutes=fake.random_int(min=5, max=60)) if fake.boolean(chance_of_getting_true=70) else None
    # )


class CardStudyDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CardStudyData

    card = factory.SubFactory(CardFactory)
    user = factory.SubFactory(UserFactory)
    ease_factor = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=1.3, max_value=3.0))
    interval = factory.LazyAttribute(lambda _: fake.random_int(min=0, max=30))
    last_reviewed = factory.LazyFunction(lambda: timezone.now() - timedelta(days=fake.random_int(min=0, max=10)))
    next_review = factory.LazyAttribute(
        lambda obj: obj.last_reviewed + timedelta(days=obj.interval)
    )
    total_reviews = factory.LazyAttribute(lambda _: fake.random_int(min=0, max=50))
