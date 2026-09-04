# Muller's Firearms Frontend

Клиентская часть демонстрационного интернет-магазина на React и Vite.

Полная инструкция запуска находится в [корневом README](../README.md).

```bash
npm ci
npm run dev
```

Vite открывает приложение на <http://localhost:5173> и проксирует запросы
`/api` на FastAPI по адресу <http://localhost:8000>.

Проверки production-сборки:

```bash
npm run lint
npm run build
```
