# Product Reviews Demo

Микросервисное демо: FastAPI API + worker на очереди RabbitMQ + статичный фронт. Отзывы уходят на ML‑модерацию (русские модели токсичности и спама), только прошедшие модерацию отображаются.

## Структура
- `api/` — FastAPI, REST CRUD для товаров и отзывов, продюсер сообщений в очередь. Общий код подтягивает из `common/`.
- `worker/` — консюмер RabbitMQ, проверяет текст отзывов готовыми русскоязычными моделями (`s-nlp/russian_toxicity_classifier`, `RUSpam/spam_deberta_v4`) и выставляет статус/причину.
- `frontend/` — HTML/JS (Manrope, тёмная тема), страницы списка/создания товара и карточки товара с формой отзывов.
- `common/` — shared модели/CRUD/конфиг/DB.
- `db` — PostgreSQL.
- `rabbitmq` — брокер + UI на `http://localhost:15672` (guest/guest).

## Быстрый старт
```bash
docker-compose up --build
```
После запуска:
- API: http://localhost:8000 (Swagger /docs)
- Frontend: http://localhost:8080
- RabbitMQ UI: http://localhost:15672 (guest/guest)

## API основные маршруты
- `POST /products`, `GET /products`, `GET /products/{id}`, `PUT /products/{id}`, `DELETE /products/{id}`
- `POST /reviews/publish` — создать отзыв, статус `pending`, улетает в очередь
- `PUT /reviews/{id}` — обновить отзыв, снова `pending`
- `GET /reviews?product_id=...&published_only=true`

В ответах отзывов есть `moderation_reason` — причина отклонения (если статус `rejected`).

## Конфигурация
Все переменные в `.env`:
`DB_*`, `RABBIT_*`, `RABBIT_QUEUE`. Docker‑сервисы используют их автоматически.

## Модерация
Worker грузит модели из HuggingFace:
- токсичность: `s-nlp/russian_toxicity_classifier`
- спам: `RUSpam/spam_deberta_v4`
Отзыв отклоняется, если хотя бы одна модель сработала; причина сохраняется в БД и пишется в логи.

## Схема БД
Таблицы создаются при старте API/worker. Колонки отзывов: `status` (`pending|published|rejected`) и `moderation_reason` (nullable).
