# Culinary Book

Веб-приложение «кулинарная книга»: публикация рецептов, личная книга, рейтинг, комментарии с фото. Учебный проект по ООП (БГУИР).

## Быстрый старт (Docker)

Нужны только **Docker** и **Docker Compose**.

```bash
docker compose up --build
```

Откройте в браузере: **http://localhost:8080**

При первом запуске база автоматически наполняется демо-данными (10 пользователей, 10 рецептов, комментарии).

### Демо-аккаунты

| Логин | Пароль | Email |
|-------|--------|-------|
| `chef_anna` | `Demo1234!` | anna@gmail.com |
| `baker_bob` | `Demo1234!` | bob@yahoo.com |
| `admin` | `Admin1234!` | admin@culinary-book.local |
| … | `Demo1234!` | … |

Полный список логинов: `chef_anna`, `baker_bob`, `vegan_vika`, `pasta_pavel`, `sweet_sofia`, `grill_greg`, `soup_lena`, `spice_nina`, `healthy_ivan`, `home_maria`.

### Остановка

```bash
docker compose down
```

Чтобы сбросить БД и заново применить seed:

```bash
docker compose down -v
docker compose up --build
```

## Деплой на Railway

1. Создайте проект на [Railway](https://railway.app) и подключите репозиторий.
2. Добавьте сервис **MongoDB** (Plugin) в проект.
3. Добавьте сервис из **Dockerfile** (корень репозитория).
4. В переменных окружения приложения укажите:

| Переменная | Значение |
|------------|----------|
| `MONGODB_URL` | URL из MongoDB-плагина (например `${{MongoDB.MONGO_URL}}`) |
| `MONGODB_DATABASE` | `culinary_book` |
| `SECRET_KEY` | длинная случайная строка |
| `SEED_ON_STARTUP` | `true` (только для первого деплоя) |
| `PORT` | Railway подставит сам |

5. После первого успешного деплоя с данными можно поставить `SEED_ON_STARTUP=false`.

Файл `railway.toml` уже настроен на сборку через Dockerfile и healthcheck `/health`.

> **Важно:** на Railway один контейнер отдаёт и API, и фронтенд (статика через FastAPI). Отдельно запускать `scripts/` не нужно.

## Архитектура

```
┌─────────────┐     ┌──────────────────────────────┐
│   Browser   │────▶│  app (FastAPI + Frontend)    │
└─────────────┘     │  :8080 → API + static files  │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │  MongoDB (:27017 internal)   │
                    └──────────────────────────────┘
```

## Функционал

### Все пользователи
- Просмотр и поиск опубликованных рецептов
- Профиль автора (логин, **email**, рейтинг)
- Таблица рейтинга

### Регистрация
- Email (виден в профиле)
- Подтверждение пароля
- Проверка сложности пароля (8+ символов, A-Z, a-z, цифра)
- Автовход после регистрации (JWT)

### Автор
- **CRUD** своих рецептов: создание, редактирование, удаление из кабинета и редактора
- Ингредиенты, шаги с фото (URL), теги, публикация

### Читатель
- Книга рецептов, отметки шагов и недостающих ингредиентов
- **Комментарии** к чужим рецептам (текст + фото по URL)

### Администратор
- Редактирование и удаление опубликованных рецептов
- Редактирование и удаление комментариев
- Бан пользователей: забаненный пользователь не может публиковать рецепты и писать комментарии

## API (основное)

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/register` | Регистрация `{login, password, email}` |
| POST | `/authenticate` | Вход |
| GET | `/users/{id}/profile` | Публичный профиль |
| GET/POST | `/recipes/{id}/comments` | Комментарии |
| DELETE | `/comments/{id}` | Удалить свой комментарий |
| DELETE | `/recipes/{id}` | Удалить свой рецепт |
| GET | `/me` | Текущий пользователь, роль и статус бана |
| GET | `/admin/users` | Пользователи для админа |
| POST | `/admin/users/{id}/ban` | Забанить пользователя |
| POST | `/admin/users/{id}/unban` | Разбанить пользователя |
| GET | `/admin/comments` | Комментарии для админа |
| GET | `/health` | Healthcheck |

Полная документация: http://localhost:8080/docs (после запуска Docker).

## Структура проекта

```
Culinary-Book/
├── Dockerfile              # Единый образ: API + фронт
├── docker-compose.yml      # MongoDB + app
├── railway.toml
├── Backend/
│   ├── endpoints.py          # FastAPI
│   ├── seed.py               # Демо-данные
│   ├── library/src/          # Domain + Application
│   └── Infrastructure/       # MongoDB
└── Frontend/                 # HTML, CSS, JS
```

## Переменные окружения

См. `.env.example`.

## Локальная разработка без Docker (опционально)

```bash
# MongoDB
docker compose up mongodb -d

# Backend
cd Backend && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=library/src MONGODB_URL=mongodb://localhost:27017
uvicorn endpoints:app --reload --port 8000

# Frontend (отдельный порт)
cd Frontend && python3 -m http.server 5500
```

На порту 5500 API доступен по `http://localhost:8000` (см. `Frontend/config.js`).

## Тесты

```bash
cd Backend
source .venv/bin/activate
export PYTHONPATH=".:library/src"
pip install pytest pytest-asyncio pytest-cov
pytest tests/ -q --no-cov
```
