# Docker запуск

## 1. Подготовка
Скопируйте пример переменных окружения:

```bash
cp .env.example .env
```

При необходимости замените значения в `.env`.

## 2. Запуск

```bash
docker compose up --build
```

## 3. Проверка
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

## 4. Остановка

```bash
docker compose down
```

## 5. Остановка с удалением volume БД

```bash
docker compose down -v
```
