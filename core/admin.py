from django.contrib import admin
from .models import Deck, Card, StudySession, CardStudyData


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name', 'description', 'owner__email')


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('front_preview', 'back_preview', 'deck')
    list_filter = ('deck', 'created_at')
    search_fields = ('front', 'back', 'deck__name')

    def front_preview(self, obj):
        return obj.front[:50] + "..." if len(obj.front) > 50 else obj.front

    front_preview.short_description = 'Front'

    def back_preview(self, obj):
        return obj.back[:50] + "..." if len(obj.back) > 50 else obj.back

    back_preview.short_description = 'Back'


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'deck', 'started_at', 'ended_at', 'duration')
    list_filter = ('started_at', 'ended_at')
    search_fields = ('user__email', 'deck__name')

    def duration(self, obj):
        if not obj.ended_at:
            return "In progress"
        delta = obj.ended_at - obj.started_at
        minutes, seconds = divmod(delta.seconds, 60)
        return f"{minutes}m {seconds}s"

    duration.short_description = 'Duration'


@admin.register(CardStudyData)
class CardStudyDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_preview', 'ease_factor', 'interval', 'last_reviewed', 'next_review')
    list_filter = ('last_reviewed', 'next_review')
    search_fields = ('user__email', 'card__front', 'card__back')

    def card_preview(self, obj):
        return obj.card.front[:30] + "..." if len(obj.card.front) > 30 else obj.card.front

    card_preview.short_description = 'Card'
