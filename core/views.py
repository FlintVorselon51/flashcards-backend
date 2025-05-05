# core/views.py
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from .models import Deck, Card, StudySession, CardStudyData
from .serializers import (
    DeckSerializer, DeckDetailSerializer, CardSerializer,
    StudySessionSerializer, CardStudyDataSerializer,
    ReviewCardSerializer
)
from .services import SpacedRepetitionService
from .permissions import IsOwnerOrReadOnlyIfPublic


class DeckViewSet(viewsets.ModelViewSet):
    serializer_class = DeckSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnlyIfPublic]

    def get_queryset(self):
        user = self.request.user
        return Deck.objects.filter(
            models.Q(owner=user) | models.Q(is_public=True)
        ).distinct()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DeckDetailSerializer
        return DeckSerializer

    def get_object(self):
        obj = super().get_object()
        self.check_object_permissions(self.request, obj)
        return obj

    @action(detail=True, methods=['get'])
    def due_cards(self, request, pk=None):
        deck = self.get_object()

        service = SpacedRepetitionService()
        cards = service.get_due_cards(request.user, pk)
        serializer = CardSerializer(cards, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def start_session(self, request, pk=None):
        deck = self.get_object()

        session = StudySession.objects.create(
            user=request.user,
            deck=deck
        )
        serializer = StudySessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CardViewSet(viewsets.ModelViewSet):
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnlyIfPublic]

    def get_queryset(self):
        user = self.request.user
        deck_id = self.request.query_params.get('deck')

        queryset = Card.objects.filter(
            models.Q(deck__owner=user) | models.Q(deck__is_public=True)
        ).distinct()

        if deck_id:
            queryset = queryset.filter(deck__id=deck_id)

            deck_exists = Deck.objects.filter(
                models.Q(id=deck_id) &
                (models.Q(owner=user) | models.Q(is_public=True))
            ).exists()

            if not deck_exists:
                raise PermissionDenied("You don't have access to this deck")

        return queryset

    def perform_create(self, serializer):
        deck_id = self.request.data.get('deck')
        try:
            deck = Deck.objects.get(id=deck_id)
        except Deck.DoesNotExist:
            raise NotFound("Deck not found")

        if deck.owner != self.request.user:
            raise PermissionDenied("You can only add cards to your own decks.")

        serializer.save(deck=deck)

    def perform_update(self, serializer):
        deck_id = self.request.data.get('deck')
        if deck_id:
            try:
                deck = Deck.objects.get(id=deck_id)
            except Deck.DoesNotExist:
                raise NotFound("Deck not found")

            if deck.owner != self.request.user:
                raise PermissionDenied("You can only move cards to your own decks.")

        serializer.save()

    @action(detail=True, methods=['get'])
    def study_data(self, request, pk=None):
        card = self.get_object()
        try:
            study_data = CardStudyData.objects.get(card=card, user=request.user)
            serializer = CardStudyDataSerializer(study_data)
            return Response(serializer.data)
        except CardStudyData.DoesNotExist:
            return Response(
                {"detail": "No study data found for this card."},
                status=status.HTTP_404_NOT_FOUND
            )


class StudySessionViewSet(viewsets.ModelViewSet):
    serializer_class = StudySessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        return StudySession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        deck_id = self.request.data.get('deck')
        try:
            deck = Deck.objects.get(id=deck_id)
            if deck.owner != self.request.user and not deck.is_public:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You don't have permission to create a study session for this deck")
        except Deck.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Deck not found")

        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def end_session(self, request, pk=None):
        """End an active study session"""
        session = self.get_object()
        if session.ended_at is not None:
            return Response(
                {"detail": "This session has already ended."},
                status=status.HTTP_400_BAD_REQUEST
            )

        session.ended_at = timezone.now()
        session.save()
        serializer = StudySessionSerializer(session)
        return Response(serializer.data)


class ReviewCardView(generics.GenericAPIView):
    serializer_class = ReviewCardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        card_id = serializer.validated_data['card_id']
        difficulty = serializer.validated_data['difficulty']

        try:
            card = Card.objects.get(id=card_id)
            if card.deck.owner != request.user and not card.deck.is_public:
                return Response(
                    {"detail": "You don't have permission to review this card."},
                    status=status.HTTP_403_FORBIDDEN
                )

            service = SpacedRepetitionService()
            card_data = service.update_card_study_data(
                request.user, card_id, difficulty
            )

            return Response(
                CardStudyDataSerializer(card_data).data,
                status=status.HTTP_200_OK
            )

        except Card.DoesNotExist:
            return Response(
                {"detail": "Card not found."},
                status=status.HTTP_404_NOT_FOUND
            )


class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, *args, **kwargs):
        return Response({"status": "healthy"}, status=status.HTTP_200_OK)
