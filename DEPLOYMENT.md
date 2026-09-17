# Развёртывание демо на VPS

Конфигурация рассчитана на отдельный Linux-сервер с Docker Engine и Compose V2,
доменом и свободными портами 80/443. Если на сервере уже работает сайт или прокси,
сначала нужно согласовать маршрутизацию с его конфигурацией.

`docker-compose.prod.yml` запускается **самостоятельно**, без объединения с
`docker-compose.yml`. У production отдельное имя проекта и отдельные тома.
Первый запуск создаёт новый учебный каталог; локальные пользователи и фотографии
автоматически на сервер не переносятся.

## Что настроено

- Caddy принимает HTTP/HTTPS и автоматически обслуживает сертификат домена
- Nginx отдаёт React и проксирует `/api` на FastAPI
- PostgreSQL, API и внутренний Nginx не публикуют порты на сервере
- Backend работает в `production`, с выключенными debug и SQL-логами
- Миграции и первоначальное заполнение выполняются при запуске
- База, загруженные фотографии и сертификаты сохраняются в именованных томах
- Контейнеры перезапускаются после перезагрузки, журналы ограничены по размеру
- Вход и AI-запросы имеют общий лимит частоты для небольшого публичного демо

Обычный `docker-compose.yml` остаётся конфигурацией для локальной разработки.

## Домен и Docker

Установите Docker по [официальной инструкции для вашей ОС](https://docs.docker.com/engine/install/)
и проверьте `docker compose version`. Для этой конфигурации нужен Compose с
поддержкой `up --wait`.

Создайте A-запись домена или поддомена на IPv4 сервера. AAAA-запись нужна только
при настроенном рабочем IPv6. Порты 80 и 443 TCP должны быть доступны извне,
443 UDP используется для HTTP/3. Существующий SSH-доступ нужно сохранить.
Для выпуска сертификата Caddy также нужен исходящий доступ в интернет.
[Условия автоматического HTTPS](https://caddyserver.com/docs/automatic-https)

## Первоначальная настройка

На сервере:

```bash
git clone --branch portfolio-rework --single-branch https://github.com/Ghost2772/Diplom.git
cd Diplom
cp .env.production.example .env.production
chmod 600 .env.production
nano .env.production
```

Заполните `DOMAIN` (без `https://` и пути) и `ACME_EMAIL`. Для `SECRET_KEY`,
`POSTGRES_PASSWORD` и `DEMO_ADMIN_PASSWORD` сгенерируйте **три разных** значения:

```bash
openssl rand -hex 32
```

Пароль базы используется в URL подключения, поэтому для него удобна именно
hex-строка. `DEMO_ADMIN_EMAIL` — адрес для вашего административного входа;
посетители используют отдельную кнопку демо. `.env.production` исключён из Git.
Пустые обязательные значения остановят Compose до создания контейнеров.

Если нужен AI, добавьте `GIGACHAT_AUTH_KEY` и настройте сертификат по
[инструкции в README](README.md#подключение-gigachat), записывая значения в
`.env.production`. Сертификат скачайте **до сборки backend**. Ключ остаётся только
на сервере, проверка TLS включена. Без ключа остальные разделы продолжают работать.

В `deploy/nginx.conf` установлены общие для всех посетителей бюджеты: 30 POST
запросов в минуту на вход, регистрацию и создание демо-сессий; 10 — на ответы AI.
Допускаются короткие серии запросов, превышение возвращает JSON с HTTP 429.
Чтение конфигурации демо и истории чата не расходует эти бюджеты.
Это ограничение частоты, а не суточный лимит расходов: квоту GigaChat нужно
настроить отдельно в используемом проекте API.
[Механизм ограничения запросов Nginx](https://nginx.org/en/docs/http/ngx_http_limit_req_module.html)

## Запуск и проверка

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml config --quiet
docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build --wait --wait-timeout 180
docker compose --env-file .env.production -f docker-compose.prod.yml ps
```

У `db`, `backend` и `frontend` должен быть статус `healthy`, у `gateway` — `Up`.
`--wait` проверяет контейнеры; получение публичного сертификата проверяется
отдельным открытием сайта. Замените домен в следующих командах на свой:

```bash
curl -I http://demo.example.com
curl -fsS https://demo.example.com/api/health
```

Первая команда должна показать перенаправление на HTTPS, вторая —
`{"status":"ok","environment":"production"}`. Затем откройте `/about`,
войдите в демо, проверьте товар → корзину → заказ, чат и административный вход.
Swagger доступен по `/api/docs`.

Если сервис не запустился или сертификат ещё не получен:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml logs --tail=100 gateway frontend backend
```

## Обновление

Перед обновлением сохраните резервную копию данных. Затем из каталога проекта:

```bash
git pull --ff-only
docker compose --env-file .env.production -f docker-compose.prod.yml config --quiet
docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build --wait --wait-timeout 180
docker compose --env-file .env.production -f docker-compose.prod.yml exec gateway caddy reload --config /etc/caddy/Caddyfile
```

Команда `up` применяет изменения `.env.production` пересозданием нужных контейнеров.
Обычный `restart` переменные не обновляет. Пароли PostgreSQL и уже созданного
администратора не меняются простой правкой этого файла: это параметры
первоначального создания, существующий пароль нужно менять отдельно.
Изменение `SECRET_KEY` завершит ранее выданные сеансы входа.

## Резервная копия

Из корня работающего проекта в Bash:

```bash
umask 077
backup_dir="backups/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$backup_dir"
docker compose --env-file .env.production -f docker-compose.prod.yml exec -T db \
  sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$backup_dir/database.dump"
docker compose --env-file .env.production -f docker-compose.prod.yml run --rm --no-deps -T \
  --entrypoint tar backend -C /app/uploads -czf - . > "$backup_dir/uploads.tar.gz"
```

Убедитесь, что обе команды завершились успешно, и скопируйте полученную папку
на другой компьютер. `.env.production` храните отдельно в защищённом месте;
каталог `backups/` исключён из Git. Тома сохраняются при обычном обновлении и
остановке. `down -v` удаляет их, поэтому для обновления эта команда не применяется.

Конфигурации Compose, Caddy и Nginx проверяются в CI. Окончательная проверка
публичного HTTPS, DNS и пользовательских сценариев выполняется на целевом VPS.
