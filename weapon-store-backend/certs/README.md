# Сертификаты GigaChat

Поместите официальный `russian_trusted_root_ca_pem.crt` в эту папку и задайте
`GIGACHAT_CA_BUNDLE=/app/certs/russian_trusted_root_ca_pem.crt` в корневом `.env`
при запуске через Docker. Затем пересоберите backend: файл попадёт в контейнер
через `COPY` в Dockerfile. При локальном запуске укажите локальный путь к файлу.

Корневой сертификат дополняет стандартное хранилище доверия только для запросов
к GigaChat. Проверка TLS остаётся включённой.

[Инструкция и официальный источник сертификата](https://developers.sber.ru/docs/ru/gigachat/certificates)
