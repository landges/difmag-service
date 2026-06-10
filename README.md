# difmag-service

Сервис для поиска похожих изображений и отбора нечетких дублей.

Изображение преобразуется в embedding размерности `2048` через ResNet-50, экспортированную в ONNX. Embedding хранится в PostgreSQL с расширением `pgvector`, поэтому сервис можно использовать не только как дедупликатор, но и как простой поисковый движок по похожим изображениям.

## Что умеет

- Создавать профили датасетов.
- Загружать изображения в профиль.
- Проверять новое изображение на похожесть с уже загруженными.
- Возвращать лучший найденный матч при проверке.
- Искать топ похожих изображений по загруженному файлу.
- Автоматически поднимать PostgreSQL + pgvector и применять Alembic-миграции через Docker Compose.

## Архитектура

- `backend` - FastAPI-приложение.
- `postgres` - PostgreSQL 15 с pgvector.
- `migrate` - одноразовый контейнер для `alembic upgrade head`.
- `backend/models/resnet50_embedding.onnx` - ONNX-модель для получения embedding.

Runtime-контейнер не использует `torch` и `torchvision`. Они нужны только для разового экспорта ONNX-модели.

## Подготовка модели

ONNX-файл не хранится в git, потому что это большой бинарный артефакт.

Сгенерируйте модель локально:

```powershell
cd C:\Users\1\PycharmProjects\CV\difmag-service\backend
pip install -r requirements-export.txt
python scripts\export_resnet50_onnx.py
```

После экспорта должен появиться файл:

```text
backend\models\resnet50_embedding.onnx
```

По умолчанию приложение ищет модель по пути:

```text
/home/app/backend/models/resnet50_embedding.onnx
```

Путь можно переопределить переменной окружения:

```text
MYAPI_MODEL_PATH=/path/to/model.onnx
```

## Переменные окружения

Основные переменные лежат в `backend/.env`.

Минимальный пример:

```env
MYAPI_DATABASE__DSN=postgresql+psycopg2://postgres:postgres@postgres:5432/difimages
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=difimages
SQL_HOST=postgres
SQL_PORT=5432
```

Для локального подключения к БД с хоста используется порт `5434`:

```text
postgresql://postgres:postgres@localhost:5434/difimages
```

## Запуск

Из корня проекта:

```powershell
docker compose up --build
```

Сервисы:

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/health`
- PostgreSQL с хоста: `localhost:5434`

При первом старте PostgreSQL применяет init-скрипт `backend/db/initdb/init_extension.sql`, который создает расширение `vector`.

## API

Все endpoints находятся под префиксом:

```text
/api/images
```

Примеры ниже используют `curl.exe` для PowerShell.

### Создать профиль

```powershell
curl.exe -X POST "http://localhost:8000/api/images/profile/create?name=main"
```

Ответ:

```json
{
  "id": 1,
  "name": "main"
}
```

### Получить профиль

```powershell
curl.exe "http://localhost:8000/api/images/profile?name=main"
```

Ответ:

```json
{
  "id": 1,
  "name": "main",
  "images": [
    {
      "id": 1,
      "file_path": "image.jpg",
      "hash": "..."
    }
  ]
}
```

### Удалить профиль

```powershell
curl.exe -X DELETE "http://localhost:8000/api/images/profile/delete?name=main"
```

### Загрузить изображение

```powershell
curl.exe -X POST "http://localhost:8000/api/images/load?profile=main" `
  -F "file=@C:\path\to\image.jpg"
```

Ответ:

```json
{
  "status": "created",
  "image": {
    "id": 1,
    "file_path": "image.jpg",
    "hash": "..."
  }
}
```

### Проверить изображение на уникальность

```powershell
curl.exe -X POST "http://localhost:8000/api/images/check?profile=main&threshhold=0.85&uniq_create=true" `
  -F "file=@C:\path\to\candidate.jpg"
```

Параметры:

- `profile` - имя профиля.
- `threshhold` - порог похожести от `0` до `1`. В коде параметр сейчас называется именно `threshhold`.
- `uniq_create` - если `true`, уникальное изображение будет добавлено в профиль.

Если найден похожий дубль:

```json
{
  "is_unique": false,
  "max_similarity": 0.91,
  "threshold": 0.85,
  "created": false,
  "best_match": {
    "image": {
      "id": 12,
      "file_path": "original.jpg",
      "hash": "..."
    },
    "similarity": 0.91,
    "distance": 0.09
  },
  "image": null
}
```

Если изображение уникальное и `uniq_create=true`:

```json
{
  "is_unique": true,
  "max_similarity": 0.42,
  "threshold": 0.85,
  "created": true,
  "best_match": {
    "image": {
      "id": 12,
      "file_path": "closest.jpg",
      "hash": "..."
    },
    "similarity": 0.42,
    "distance": 0.58
  },
  "image": {
    "id": 13,
    "file_path": "candidate.jpg",
    "hash": "..."
  }
}
```

### Найти похожие изображения

Этот endpoint можно использовать как поисковый движок по картинке.

```powershell
curl.exe -X POST "http://localhost:8000/api/images/search?profile=main&limit=10&threshold=0.7" `
  -F "file=@C:\path\to\query.jpg"
```

Параметры:

- `profile` - имя профиля.
- `limit` - сколько похожих изображений вернуть, от `1` до `100`, по умолчанию `10`.
- `threshold` - необязательный минимальный порог похожести от `0` до `1`.

Ответ:

```json
{
  "profile": "main",
  "total": 2,
  "matches": [
    {
      "image": {
        "id": 12,
        "file_path": "original.jpg",
        "hash": "..."
      },
      "similarity": 0.91,
      "distance": 0.09
    },
    {
      "image": {
        "id": 4,
        "file_path": "another.jpg",
        "hash": "..."
      },
      "similarity": 0.78,
      "distance": 0.22
    }
  ]
}
```

## Метрики похожести

- `distance` - cosine distance из pgvector. Чем меньше, тем ближе изображения.
- `similarity` - `1 - distance`. Чем ближе к `1`, тем изображения похожее.

Для дедупликации обычно удобно начинать с порога `0.85` и дальше подбирать на своем датасете.

## Production notes

- Не коммитьте `backend/models/*.onnx` в git. Модель игнорируется через `.gitignore`.
- Для production используйте внешний секрет-хранилище вместо хранения реального `.env` в репозитории.
- PostgreSQL можно вынести из compose в отдельный кластер. В этом случае нужен PostgreSQL с установленным расширением `pgvector`.
- Runtime-образ устанавливает только `onnxruntime`, а не PyTorch, поэтому он легче и предсказуемее.

## Полезные ссылки

- [pgvector](https://github.com/pgvector/pgvector)
- [pgvector-python](https://github.com/pgvector/pgvector-python)
- [ONNX Runtime](https://onnxruntime.ai/)
