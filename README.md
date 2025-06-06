# Развёрнутое приложение
[Демо](http://flashcards.hitasher.ru)

---

# Flashcards Backend
Backend часть приложения для адаптивного запоминания информации. Реализована на Django REST Framework с использованием PostgreSQL и алгоритма SuperMemo-2.

## Основные технологии
- **Python** (v3.10+)
- **Django** (v4.2+)
- **Django REST Framework** (для API)
- **PostgreSQL** (база данных)
- **JWT** (аутентификация)
- **Docker** (контейнеризация)
- **Gunicorn** (продакшн-сервер)
- **Nginx** (API Gateway)

## Функционал API
- Аутентификация (JWT)
- Управление пользователями
- CRUD для наборов карточек (деков)
- CRUD для карточек
- Сессии изучения
- Алгоритм интервальных повторений (SuperMemo-2)

### Запуск с Docker

Убедитесь, что Docker и Docker Compose установлены
Выполните:
```bash
docker-compose up --build
```

### Документация API
После запуска сервера документация доступна по адресу:
Swagger UI: http://localhost:8000/swagger/

See also [frontend repository](https://github.com/FlintVorselon51/flashcards-frontend)
