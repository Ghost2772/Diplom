# Muller's Firearms API

Асинхронный REST API демонстрационного интернет-магазина на FastAPI,
SQLAlchemy и PostgreSQL.

Полная инструкция запуска и описание архитектуры находятся в
[корневом README](../README.md).

## Основные команды

```bash
pip install -r requirements-dev.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Проверки:

```bash
ruff check app tests alembic
pytest
alembic upgrade head --sql
```

API по умолчанию доступен на <http://localhost:8000>, интерактивная
документация — на <http://localhost:8000/docs>.
