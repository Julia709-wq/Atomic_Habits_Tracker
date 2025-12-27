# Atomic Habits Tracker

Веб-приложение для отслеживания атомарных привычек на основе Django REST Framework с интеграцией Telegram для отправки напоминаний.

## Описание проекта

Проект представляет собой REST API для управления привычками пользователей. Система позволяет создавать, редактировать и отслеживать привычки с 
возможностью настройки напоминаний через Telegram. Приложение реализует концепцию "атомарных привычек" с валидацией бизнес-логики и автоматической 
отправкой уведомлений.

## Архитектура проекта

### Структура приложения

Проект организован по модульному принципу с разделением на приложения Django:

```
Atomic_Habits_Tracker/
├── config/              # Основные настройки проекта
│   ├── settings.py      # Конфигурация Django
│   ├── urls.py          # Корневая маршрутизация
│   ├── celery.py        # Настройка Celery
│   ├── wsgi.py          # WSGI конфигурация
│   └── asgi.py          # ASGI конфигурация
├── users/               # Приложение управления пользователями
│   ├── models.py        # Модель User
│   ├── views.py         # API endpoints для регистрации
│   ├── serializers.py   # Сериализаторы пользователей
│   └── urls.py          # Маршруты пользователей
├── tracker/             # Приложение отслеживания привычек
│   ├── models.py        # Модель Habit
│   ├── views.py         # ViewSet для CRUD операций
│   ├── serializers.py   # Сериализаторы привычек
│   ├── validators.py    # Валидаторы бизнес-логики
│   ├── permissions.py   # Кастомные права доступа
│   ├── services.py      # Сервисы (Telegram интеграция)
│   ├── tasks.py         # Celery задачи
│   ├── paginators.py    # Пагинация
│   └── urls.py          # Маршруты привычек
└── manage.py            # Django management script
```

### Архитектурные компоненты

#### 1. **Django REST Framework (DRF)**
- RESTful API для взаимодействия с клиентскими приложениями
- JWT аутентификация через `djangorestframework-simplejwt`
- Swagger/ReDoc документация через `drf-yasg`
- Пагинация результатов запросов

#### 2. **База данных PostgreSQL**
- Реляционная БД для хранения пользователей и привычек
- Миграции Django для управления схемой БД

#### 3. **Celery + Redis**
- **Celery**: Асинхронная обработка задач
- **Redis**: Брокер сообщений и хранилище результатов
- **django-celery-beat**: Планировщик периодических задач
- Автоматическая отправка напоминаний о привычках через Telegram

#### 4. **Telegram Bot API**
- Интеграция с Telegram для отправки уведомлений
- Отправка напоминаний пользователям в указанное время

## Зависимости проекта

### Основные зависимости

```txt
Django==5.2.9                    # Веб-фреймворк
djangorestframework==3.16.1      # REST API фреймворк
djangorestframework-simplejwt==5.5.1  # JWT аутентификация
```

### База данных

```txt
psycopg2-binary==2.9.11          # PostgreSQL адаптер для Python
```

### Асинхронные задачи

```txt
celery==5.6.0                    # Распределенная очередь задач
django-celery-beat==2.8.1        # Планировщик задач для Django
redis==7.1.0                     # Redis клиент
kombu==5.6.1                     # Библиотека обмена сообщениями
billiard==4.2.4                  # Многопроцессорность для Celery
```

### Документация API

```txt
drf-yasg==1.21.11                # Swagger/OpenAPI генератор
PyYAML==6.0.3                    # Парсер YAML
uritemplate==4.2.0               # Шаблоны URI
inflection==0.5.1                # Склонение слов
```

### Внешние интеграции

```txt
requests==2.32.5                 # HTTP клиент для Telegram API
```

### Утилиты

```txt
python-dotenv==1.2.1             # Загрузка переменных окружения
django-cors-headers==4.9.0       # CORS поддержка
django-timezone-field==7.2.1     # Поля часовых поясов
pytz==2025.2                     # Работа с часовыми поясами
python-dateutil==2.9.0.post0     # Парсинг дат
```

### Вспомогательные библиотеки

```txt
click==8.3.1                     # CLI утилиты
cron-descriptor==2.0.6           # Описание cron выражений
python-crontab==3.3.0            # Работа с crontab
```

## Модели данных

### User (users/models.py)

Кастомная модель пользователя на основе `AbstractUser`:
- `email` - уникальный email (используется для входа)
- `tg_chat_id` - идентификатор Telegram чата для уведомлений
- Аутентификация по email вместо username

### Habit (tracker/models.py)

Модель привычки со следующими полями:
- `owner` - владелец привычки (ForeignKey к User)
- `action` - описание действия (макс. 300 символов)
- `place` - место выполнения (макс. 200 символов, опционально)
- `time_of_day` - время выполнения (TimeField, опционально)
- `is_pleasant` - флаг приятной привычки
- `related_habit` - связанная приятная привычка (ForeignKey к себе)
- `reward` - вознаграждение (макс. 300 символов, опционально)
- `period_days` - периодичность выполнения (1-7 дней)
- `duration_seconds` - длительность выполнения (макс. 120 секунд)
- `is_public` - флаг публичности привычки
- `created_at`, `updated_at` - временные метки

## Бизнес-логика и валидация

### Правила валидации привычек (tracker/validators.py)

1. **Время выполнения**: не более 120 секунд
2. **Периодичность**: от 1 до 7 дней
3. **Взаимоисключающие поля**: нельзя указать одновременно `reward` и `related_habit`
4. **Приятная привычка**: не может иметь вознаграждения или связанной привычки
5. **Связанная привычка**: должна быть приятной (`is_pleasant=True`)
6. **Самосвязь**: привычка не может быть связана сама с собой

## API Endpoints

### Аутентификация (users/urls.py)

- `POST /users/register/` - Регистрация нового пользователя
- `POST /users/login/` - Получение JWT токенов (access + refresh)
- `POST /users/token/refresh/` - Обновление access токена

### Привычки (tracker/urls.py)

- `GET /api/tracker/habits/` - Список привычек текущего пользователя (с пагинацией)
- `POST /api/tracker/habits/` - Создание новой привычки
- `GET /api/tracker/habits/{id}/` - Детали привычки
- `PUT /api/tracker/habits/{id}/` - Полное обновление привычки
- `PATCH /api/tracker/habits/{id}/` - Частичное обновление привычки
- `DELETE /api/tracker/habits/{id}/` - Удаление привычки
- `GET /api/tracker/habits/public/` - Список публичных привычек

### Документация

- `GET /swagger/` - Swagger UI документация
- `GET /redoc/` - ReDoc документация

## Права доступа

### IsAuthenticated
Все endpoints требуют аутентификации через JWT токен (кроме регистрации).

### IsOwnerOrReadOnly (tracker/permissions.py)
- Чтение: доступно всем аутентифицированным пользователям
- Изменение/Удаление: только владельцу привычки

## Работа системы

### 1. Регистрация и аутентификация

1. Пользователь регистрируется через `POST /users/register/` с email и password
2. При входе через `POST /users/login/` получает пару JWT токенов:
   - `access` токен (срок жизни: 1 день) - для авторизации запросов
   - `refresh` токен (срок жизни: 7 дней) - для обновления access токена
3. В заголовке запросов передается: `Authorization: Bearer <access_token>`

### 2. Управление привычками

1. Пользователь создает привычку через `POST /api/tracker/habits/`
2. Система автоматически валидирует данные согласно бизнес-правилам
3. Привычка привязывается к текущему пользователю
4. Пользователь может просматривать только свои привычки
5. Публичные привычки доступны всем через endpoint `/public/`

### 3. Система напоминаний (Celery)

#### Настройка Celery

- **Брокер**: Redis (CELERY_BROKER_URL)
- **Backend**: Redis (CELERY_DEFAULT_BACKEND)
- **Планировщик**: django-celery-beat с PersistentScheduler
- **Расписание**: задача выполняется каждую минуту (`crontab(minute='*')`)

#### Процесс отправки напоминаний

1. **Периодическая задача** (`tracker/tasks.py::send_reminder_notification`):
   - Запускается каждую минуту через Celery Beat
   - Получает текущее время в часовом поясе проекта (Europe/Moscow)
   - Находит все привычки с указанным `time_of_day`

2. **Проверка времени**:
   - Сравнивает текущее время с временем привычки
   - Отправляет напоминание, если разница ≤ 1 минуты

3. **Отправка в Telegram** (`tracker/services.py::send_tg_reminder`):
   - Формирует сообщение с описанием привычки
   - Отправляет через Telegram Bot API
   - Требует наличия `tg_chat_id` у пользователя

#### Формат сообщения

```
! Напоминание о привычке!

Я буду {action} в {place} в {time}.
Время выполнения: {duration_seconds} секунд.
Вознаграждение: {reward} / После выполнения: {related_habit.action}
```

### 4. Пагинация

- Размер страницы: 5 записей
- Параметр: `?page_size=5` (максимум 5)
- Параметр: `?page=1` для навигации

## Переменные окружения

Создайте файл `.env` на основе `example.env`:

```env
SECRET_KEY=your-secret-key
DEBUG=True
PROJECT_NAME=Atomic_Habits_Tracker
NAME=your-db-name
USER=your-db-user
PASSWORD=your-db-password
HOST=localhost
PORT=5432
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_DEFAULT_BACKEND=redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/0
TELEGRAM_BOT_URL=your-telegram-bot-token
```

## Установка и запуск

### 1. Клонирование и настройка окружения

```bash
# Создание виртуального окружения
python -m venv env

# Активация (Windows)
env\Scripts\activate

# Активация (Linux/Mac)
source env/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Настройка базы данных

```bash
# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser
```

### 3. Запуск Redis

Убедитесь, что Redis запущен и доступен по адресу из `.env`.

### 4. Запуск приложения

```bash
# Запуск Django сервера
python manage.py runserver

# В отдельном терминале - запуск Celery worker
celery -A config worker -l info

# В отдельном терминале - запуск Celery beat (планировщик)
celery -A config beat -l info
```

### 5. Доступ к API

- API: `http://localhost:8000/`
- Swagger: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`
- Admin: `http://localhost:8000/admin/`

## Особенности реализации

### Валидация на уровне модели

Валидация выполняется автоматически при сохранении через метод `save()` модели `Habit`, который вызывает `full_clean()`. Это гарантирует валидацию независимо от источника данных (API, админ-панель, shell).

### Обработка часовых поясов

Система использует часовой пояс `Europe/Moscow` для корректной работы с временем выполнения привычек. Celery задачи учитывают локальный часовой пояс при проверке времени.

### Логирование

Все операции отправки напоминаний логируются для отладки и мониторинга:
- Проверка времени
- Отправка сообщений
- Ошибки при работе с Telegram API

### Windows совместимость

Celery настроен для работы на Windows через использование `solo` pool вместо `prefork` (см. `config/celery.py`).

## Технологический стек

- **Backend**: Django 5.2.9, Django REST Framework 3.16.1
- **База данных**: PostgreSQL
- **Очередь задач**: Celery 5.6.0, Redis 7.1.0
- **Аутентификация**: JWT (djangorestframework-simplejwt)
- **Документация**: Swagger/OpenAPI (drf-yasg)
- **Внешние API**: Telegram Bot API

## Лицензия

Проект создан в образовательных целях.

