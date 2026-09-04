# Backend-only Docker Compose

Основной сценарий запуска всего приложения описан в
[корневом README](../README.md) и использует `docker-compose.yml` в корне.

Для запуска только FastAPI и PostgreSQL:

```bash
docker compose up --build
```

Команда выполняется из каталога `weapon-store-backend`. API и Swagger будут
доступны на <http://localhost:8000> и <http://localhost:8000/docs>.
