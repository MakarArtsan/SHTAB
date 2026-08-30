# ШТАБ

Веб-платформа координации наблюдателей на выборах. Наблюдатель на участке работает
с телефона, штаб — с большого экрана; код один. Приложение обязано работать без сети.

Полное описание — в [`docs/ТЗ.md`](docs/ТЗ.md). Правила разработки — в [`CLAUDE.md`](CLAUDE.md).
Что сделано и что дальше — в [`docs/ПЛАН.md`](docs/ПЛАН.md) и [`docs/ВЫПОЛНЕНИЕ.md`](docs/ВЫПОЛНЕНИЕ.md).

## Запуск за пять минут

Нужен только Docker (Desktop или Engine) и `make`. Ни Python, ни Node ставить не нужно —
всё работает в контейнерах.

```bash
git clone https://github.com/MakarArtsan/SHTAB.git
cd SHTAB
make up
```

Первый запуск занимает 3–5 минут: собираются образы и ставятся зависимости.
Файл `.env` создастся сам из `.env.example`, править его для локальной работы не нужно.

Когда команда закончится:

| Что | Адрес |
|---|---|
| Приложение | http://localhost:5173 |
| API | http://localhost:8000/health |
| Документация API | http://localhost:8000/docs |
| Консоль хранилища MinIO | http://localhost:9001 |

Проверка, что всё поднялось:

```bash
curl http://localhost:8000/health
# {"status":"ok","service":"shtab-api","env":"local"}
```

## Команды

```bash
make up        # поднять всё локально
make down      # остановить
make logs      # логи api и web
make migrate   # накатить миграции Alembic
make seed      # тестовые данные
make test      # pytest + vitest
make lint      # ruff + mypy + eslint + tsc
```

`make` без аргументов покажет этот список.

## Что внутри

```
/api    FastAPI, Python 3.12, SQLAlchemy 2.0 async, Alembic, Pydantic v2
/web    PWA: React 18, TypeScript strict, Vite, Tailwind, shadcn/ui
/infra  docker-compose для разработки и для продакшна, Caddyfile, образ PostgreSQL
/docs   ТЗ, план, журнал выполнения, промпты и инструкция
/data   справочники: категории инцидентов и далее по плану
```

PostgreSQL 16 собирается своим образом: к PostGIS добавляется `pgvector`, плюс включаются
`ltree` и `pg_trgm`. Redis — для WebSocket, очередей и кэша. MinIO подменяет S3 локально.

## Если что-то не поднялось

- **Порт занят.** Поменяйте `API_PORT`, `WEB_PORT`, `POSTGRES_PORT` в `.env` и повторите `make up`.
- **Web долго стартует.** Первый запуск ставит зависимости npm внутри контейнера. Смотрите `make logs`.
- **Нужно начать с чистого листа.** `docker compose -f infra/docker-compose.yml down -v` удалит тома с данными.

## Продакшн

Локально обратного прокси нет — `api` и `web` открыты напрямую. Для сервера в `/infra`
лежат `docker-compose.prod.yml` и `Caddyfile`: Caddy получает сертификат сам, раздаёт
собранную статику и проксирует `/api`, `/ws` и `/health` на бэкенд.

```bash
# на сервере, после заполнения .env (DOMAIN, ACME_EMAIL, пароли)
docker compose -f infra/docker-compose.prod.yml --env-file .env up -d --build
```

Секреты в репозиторий не коммитим: в git лежит только `.env.example`.
