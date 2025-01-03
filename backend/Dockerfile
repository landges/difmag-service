###########
# BUILDER #
###########
FROM python:3.9-slim as builder

# Устанавливаем системные пакеты, необходимые для компиляции зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libmagic-dev \
    file \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Создаём рабочую директорию
WORKDIR /usr/src/app

# Обновляем pip
RUN pip install --upgrade pip

# Копируем список зависимостей
COPY requirements.txt .

# Собираем колёса (wheel) всех зависимостей в папку wheels
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


#########
# FINAL #
#########
FROM python:3.9-slim

# Для корректной работы tzdata (установка часового пояса)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    libpq-dev \
    libmagic-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем часовой пояс
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Создаём директорию для приложения и пользователя
RUN mkdir -p /home/app
RUN addgroup --system app && adduser --system --ingroup app app

# Настройки Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Создаём рабочую директорию приложения
ENV HOME=/home/app
ENV APP_HOME=/home/app/backend
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# Копируем собранные колёса из builder-этапа и устанавливаем их
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir /wheels/*

# Копируем исходный код приложения
COPY . $APP_HOME

# Делаем владельцем папки пользователя app
RUN chown -R app:app $APP_HOME

# Переходим под пользователя app
USER root

EXPOSE 8000

# Запускаем FastAPI (пример с uvicorn)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
