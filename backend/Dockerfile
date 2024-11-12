###########
# BUILDER #
###########

# pull official base image
FROM python:3.9.6-alpine as builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev file libmagic

# lint
RUN pip install --upgrade pip
# COPY . .

# install dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


#########
# FINAL #
#########

# pull official base image
FROM python:3.9.6-alpine

# install tzdata
RUN apk update && apk add --no-cache tzdata curl

# set timezone
ENV TZ=Europe/Moscow
RUN cp /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup -S app && adduser -S app -G app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/backend
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# install dependencies
RUN apk update && apk add libpq

# Устанавливаем Docker CLI
RUN apk add --no-cache docker-cli file libmagic
ARG DOCKER_GID=1001

# Создаем группу docker в контейнере с тем же GID
RUN addgroup -g ${DOCKER_GID} docker && adduser app docker

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

COPY entrypoint.sh .
RUN sed -i 's/\r$//g'  $APP_HOME/entrypoint.sh
RUN chmod +x  $APP_HOME/entrypoint.sh

# copy project
COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R app:app $APP_HOME
RUN pip install --editable .

# change to the app user
USER root
EXPOSE 8000

# CMD python app/main.py
# CMD [ "uvicorn app.main:app" ]
# ENTRYPOINT ["./entrypoint.sh"]
# ENTRYPOINT ["./entrypoint.prod.sh"]
RUN sed -i 's/%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s] - %(message)s/%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s] - %(message)s/g' /usr/local/lib/python3.9/site-packages/uvicorn/config.py

# Запускаем приложение
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
