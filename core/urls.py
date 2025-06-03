from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeckViewSet, CardViewSet, StudySessionViewSet, ReviewCardView, HealthCheckView

router = DefaultRouter()
router.register(r'decks', DeckViewSet, basename='deck')
router.register(r'cards', CardViewSet, basename='card')
router.register(r'sessions', StudySessionViewSet, basename='session')

app_name = 'core'

urlpatterns = [
    path('', include(router.urls)),
    path('review/', ReviewCardView.as_view(), name='review'),
    path('health/', HealthCheckView.as_view(), name='health-check'),
]
