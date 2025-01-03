# Базовый образ PostgreSQL 15
FROM postgres:15

# Устанавливаем pgvector для PostgreSQL 15
RUN apt-get update && apt-get install -y postgresql-15-pgvector

# Копируем скрипты инициализации в контейнер
# Всё, что положим в /docker-entrypoint-initdb.d/, выполнится при первом старте
COPY ./initdb/ /docker-entrypoint-initdb.d/
