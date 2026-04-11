# 🛒 Weapon Store Backend with AI Consultant

Дипломный проект: backend интернет-магазина охотничьего/оружейного с ИИ-консультантом.

---

## 📌 Описание

Серверная часть интернет-магазина, реализованная на FastAPI.  
Проект демонстрирует современный подход к разработке web-приложений с использованием REST API, JWT-аутентификации и интеграции с AI-сервисом (GigaChat).

---

## 🚀 Функционал

### 👤 Пользователи
- Регистрация
- Авторизация (JWT)
- Ролевая модель (admin / user)

### 🛍 Каталог
- Категории товаров
- Товары
- Поиск и фильтрация (цена, категория, активность)
- Просмотр списка и деталей

### 🧺 Корзина
- Добавление товаров
- Удаление товаров
- Очистка корзины

### 📦 Заказы
- Оформление заказа из корзины
- Просмотр заказов
- Управление статусами (admin)

### 🤖 AI-консультант
- Интеграция с GigaChat API
- Работа с реальными данными из БД
- Контекст диалога
- История сообщений
- Защита от опасных запросов

---

## 🛠 Технологии

- FastAPI
- PostgreSQL
- SQLAlchemy (async)
- JWT (python-jose)
- Pydantic
- httpx (GigaChat API)
- Docker + Docker Compose

---

## 📂 Структура проекта
app/
├── ai/ # AI-консультант
├── auth/ # Авторизация и безопасность
├── core/ # Конфигурация и БД
├── models/ # ORM модели
├── routers/ # API endpoints
├── schemas/ # Pydantic схемы
├── services/ # Бизнес-логика
└── main.py # Точка входа

---

## ⚙️ Запуск проекта

### 🔹 1. Локальный запуск (без Docker)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload

Открыть:

http://localhost:8000/docs

### 🔹2. Запуск через Docker (рекомендуется)
docker compose up --build

Открыть:

http://localhost:8000/docs

🔐 Переменные окружения

Создать файл .env:

DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/weapon_store
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

GIGACHAT_AUTH_KEY=your_key
GIGACHAT_SCOPE=GIGACHAT_API_PERS
GIGACHAT_MODEL=GigaChat-2
GIGACHAT_AUTH_URL=https://ngw.devices.sberbank.ru:9443/api/v2/oauth
GIGACHAT_API_URL=https://gigachat.devices.sberbank.ru/api/v1/chat/completions

📖 API документация

Swagger доступен по адресу:

http://localhost:8000/docs

📦 Статус проекта

✅ Backend: готов (~99%)
✅ Docker: настроен
🚧 Frontend: в разработке
🚧 Деплой: планируется

🎓 Назначение проекта

Данный проект разработан в рамках дипломной работы и демонстрирует:

разработку REST API
работу с базой данных PostgreSQL
реализацию JWT-аутентификации
интеграцию AI в бизнес-логику приложения
контейнеризацию с помощью Docker

👨‍💻 Автор

Студент ЭФБО 05-22 Абрамов Максим
