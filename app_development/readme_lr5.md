# Инструкция по запуску проекта (ЛР5)

## Шаги для запуска

### 1. Запуск контейнеров Docker

Соберите и запустите контейнеры с помощью Docker Compose:

```bash
docker compose up --build
```

Эта команда:
- Соберет Docker-образ приложения
- Запустит контейнеры PostgreSQL и веб-приложения
- Дождется готовности базы данных перед запуском приложения

### 2. Инициализация базы данных

После успешного запуска контейнеров инициализируйте базу данных:

```bash
docker exec app_web python init_db.py
```

Эта команда создаст необходимые таблицы и добавит тестовые данные.

### 3. Проверка работы API

Получите список всех пользователей:

```bash
curl http://localhost:8000/users
```

### 4. Создание нового пользователя

Создайте нового пользователя с помощью POST-запроса:

```bash
curl -X POST http://localhost:8000/users ^
  -H "Content-Type: application/json" ^
  -d "{\"username\": \"john_doe\", \"email\": \"john@example.com\", \"full_name\": \"John Doe\"}"
```

Для Linux/Mac используйте `\` вместо `^` для переноса строк:

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "email": "john@example.com", "full_name": "John Doe"}'
```

## Дополнительные команды

### Просмотр логов контейнера
```bash
docker logs app_web
```

### Остановка контейнеров
```bash
docker compose down
```

### Интерактивная документация API
Откройте в браузере:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Порты

- **8000** - веб-приложение (FastAPI)
- **5432** - база данных PostgreSQL
