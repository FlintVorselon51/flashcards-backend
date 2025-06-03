from rest_framework import serializers
from .models import Deck, Card, StudySession, CardStudyData


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['id', 'deck', 'front', 'back', 'created_at', 'updated_at']

    def validate(self, attrs):
        if self.context['request'].method in ['POST', 'PUT']:
            for field in ['front', 'back', 'deck']:
                if field not in attrs:
                    raise serializers.ValidationError({field: "This field is required."})
        return attrs


class DeckSerializer(serializers.ModelSerializer):
    cards_count = serializers.SerializerMethodField()
    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = Deck
        fields = ['id', 'name', 'description', 'owner', 'owner_email', 'is_public',
                  'created_at', 'updated_at', 'cards_count']
        read_only_fields = ['owner', 'owner_email']

    @staticmethod
    def get_cards_count(obj):
        return obj.cards.count()

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class DeckDetailSerializer(DeckSerializer):
    cards = CardSerializer(many=True, read_only=True)

    class Meta(DeckSerializer.Meta):
        fields = DeckSerializer.Meta.fields + ['cards']


class CardStudyDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardStudyData
        fields = ['id', 'ease_factor', 'interval', 'last_reviewed',
                  'next_review', 'total_reviews']
        read_only_fields = ['id', 'total_reviews']


class StudySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudySession
        fields = ['id', 'deck', 'started_at', 'ended_at']
        read_only_fields = ['started_at']


class ReviewCardSerializer(serializers.Serializer):
    card_id = serializers.IntegerField()
    difficulty = serializers.ChoiceField(choices=CardStudyData.DIFFICULTY_CHOICES)
