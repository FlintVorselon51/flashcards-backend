import random
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Deck, Card

User = get_user_model()


class Command(BaseCommand):
    help = 'Заполняет базу данных начальными данными'

    def handle(self, *args, **kwargs):
        self.stdout.write('Удаление старых данных...')
        call_command('flush', '--noinput')

        # Создание пользователей
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='1234'
        )

        empty_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='1234'
        )

        self.stdout.write(self.style.SUCCESS('Пользователи созданы!'))

        # Создание наборов карточек
        chinese_to_russian = Deck.objects.create(
            name='Китайский - Русский',
            description='Перевод китайских иероглифов на русский язык',
            owner=admin,
            is_public=True
        )

        chinese_to_pinyin = Deck.objects.create(
            name='Китайский - Пиньинь',
            description='Перевод китайских иероглифов на пиньинь',
            owner=admin,
            is_public=True
        )

        english_to_russian = Deck.objects.create(
            name='Английский - Русский B2',
            description='Перевод английских слов уровня B2 на русский',
            owner=admin,
            is_public=False
        )

        self.stdout.write(self.style.SUCCESS('Наборы карточек созданы!'))

        # Карточки для китайского языка (иероглифы - русский и иероглифы - пиньинь)
        chinese_words = [
            ('你好', 'Привет', 'nǐ hǎo'),
            ('谢谢', 'Спасибо', 'xiè xiè'),
            ('再见', 'До свидания', 'zài jiàn'),
            ('请', 'Пожалуйста', 'qǐng'),
            ('对不起', 'Извините', 'duì bù qǐ'),
            ('没关系', 'Ничего страшного', 'méi guān xi'),
            ('我', 'Я', 'wǒ'),
            ('你', 'Ты', 'nǐ'),
            ('我们', 'Мы', 'wǒ men'),
            ('他', 'Он', 'tā'),
            ('她', 'Она', 'tā'),
            ('爱', 'Любить', 'ài'),
            ('吃', 'Есть, кушать', 'chī'),
            ('喝', 'Пить', 'hē'),
            ('说', 'Говорить', 'shuō'),
            ('看', 'Смотреть', 'kàn'),
            ('听', 'Слушать', 'tīng'),
            ('学习', 'Учиться', 'xué xí'),
            ('工作', 'Работать', 'gōng zuò'),
            ('一', 'Один', 'yī'),
        ]

        # Карточки для английского языка (английский - русский, уровень B2)
        english_russian_words = [
            ('to contemplate', 'созерцать, размышлять'),
            ('ambiguous', 'двусмысленный, неоднозначный'),
            ('resilience', 'устойчивость, эластичность'),
            ('nuance', 'нюанс, тонкость'),
            ('paradigm', 'парадигма, модель'),
            ('arbitrary', 'произвольный, случайный'),
            ('intricate', 'сложный, запутанный'),
            ('pragmatic', 'прагматичный, практичный'),
            ('obsolete', 'устаревший, вышедший из употребления'),
            ('diligent', 'прилежный, старательный'),
            ('subsequent', 'последующий, следующий'),
            ('scrutinize', 'тщательно изучать, внимательно рассматривать'),
            ('articulate', 'четко выражать, членораздельно говорить'),
            ('brevity', 'краткость, лаконичность'),
            ('elusive', 'ускользающий, трудноуловимый'),
            ('notorious', 'печально известный'),
            ('perceive', 'воспринимать, понимать'),
            ('lucid', 'ясный, понятный'),
            ('mundane', 'обыденный, мирской'),
            ('profound', 'глубокий, основательный'),
        ]

        # Создание карточек в базе данных
        for hanzi, russian, pinyin in chinese_words:
            # Создаем карточку иероглиф-русский
            Card.objects.create(
                deck=chinese_to_russian,
                front=hanzi,
                back=russian
            )

            # Создаем карточку иероглиф-пиньинь
            Card.objects.create(
                deck=chinese_to_pinyin,
                front=hanzi,
                back=pinyin
            )

        for english, russian in english_russian_words:
            Card.objects.create(
                deck=english_to_russian,
                front=english,
                back=russian
            )

        self.stdout.write(self.style.SUCCESS('Карточки успешно созданы!'))
        self.stdout.write(self.style.SUCCESS('База данных успешно заполнена!'))
