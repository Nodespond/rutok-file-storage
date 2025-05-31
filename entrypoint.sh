#!/bin/sh
set -e

until pg_isready -h "postgres-db" -U "rutok" -d "rutok"; do
  echo "Ждем готовности БД..."
  sleep 3
done

echo "База данных готова. Применяем миграции..."
alembic upgrade head  # применяем последнюю миграцию

echo "Запускаем приложение..."
exec "$@"