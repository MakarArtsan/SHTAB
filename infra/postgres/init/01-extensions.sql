-- Расширения включаются один раз при создании кластера.
-- Схему таблиц создаёт Alembic, здесь только то, что миграция включить не может.
CREATE EXTENSION IF NOT EXISTS ltree;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;
