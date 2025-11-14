# API Управления Пользователями

Это REST API приложение, построенное с использованием Litestar и SQLAlchemy для управления пользователями, продуктами и заказами.

## Установка и Настройка

1. Создание и активация виртуального окружения:
```bash
python -m venv venv
.\venv\Scripts\activate  # для Windows
source venv/bin/activate  # для Linux/Mac
```

2. Установка зависимостей:
```bash
pip install -r requirements.txt
```

3. Инициализация базы данных:
```bash
python init_db.py
```

4. Запуск приложения:
```bash
python -m app.main
```

Сервер запустится по адресу `http://127.0.0.1:8000`

## Тестирование

### Запуск всех тестов:
```bash
.\venv\Scripts\python.exe -m pytest -v
```

### Запуск тестов по категориям:
```bash
# Тесты репозиториев
.\venv\Scripts\python.exe -m pytest test_user_repository.py -v
.\venv\Scripts\python.exe -m pytest test_order_repository.py -v

# Тесты эндпоинтов
.\venv\Scripts\python.exe -m pytest test_user_endpoints.py -v

# Тест пагинации
.\venv\Scripts\python.exe -m pytest test_product_pagination.py -v
```

### Запуск конкретного теста:
```bash
# Пример: тест создания пользователя
.\venv\Scripts\python.exe -m pytest test_user_repository.py::TestUserRepository::test_create_user -v

# Пример: тест эндпоинта GET
.\venv\Scripts\python.exe -m pytest test_user_endpoints.py::test_get_user_by_id_success -v
```

### Запуск с дополнительной информацией:
```bash
# С выводом print-statements
.\venv\Scripts\python.exe -m pytest test_user_repository.py -v -s

# С подробным выводом ошибок
.\venv\Scripts\python.exe -m pytest test_user_repository.py -v --tb=long

# Остановить выполнение при первой ошибке
.\venv\Scripts\python.exe -m pytest -v -x
```

**Доступные тесты:**
- `test_user_repository.py` - тесты репозитория пользователей (создание, поиск по email, обновление)
- `test_user_endpoints.py` - тесты HTTP эндпоинтов (GET, POST, PUT, DELETE)
- `test_order_repository.py` - тесты edge-cases для заказов (множественные продукты, дубликаты, несуществующие ID)
- `test_product_pagination.py` - тест пагинации товаров (проверка смещения, граничные случаи)

## API Endpoints (Конечные точки API)

API Endpoints - это URL-адреса, по которым можно выполнять различные операции с данными. В нашем приложении доступны следующие endpoints:

### 1. Получение списка пользователей
- Метод: `GET`
- URL: `http://127.0.0.1:8000/users`
- Описание: Возвращает список всех пользователей
- Как использовать: Просто откройте URL в браузере или выполните GET-запрос

### 2. Получение конкретного пользователя
- Метод: `GET`
- URL: `http://127.0.0.1:8000/users/{user_id}`
- Описание: Возвращает информацию о пользователе по его ID
- Пример: `http://127.0.0.1:8000/users/1` - получить пользователя с ID=1

### 3. Создание нового пользователя
- Метод: `POST`
- URL: `http://127.0.0.1:8000/users`
- Тело запроса (пример):
```json
{
    "username": "ivan_ivanov",
    "email": "ivan@example.com",
    "first_name": "Иван",
    "last_name": "Иванов"
}
```
- Как использовать: Отправьте POST-запрос с JSON-данными (можно использовать Postman или curl)

### 4. Обновление пользователя
- Метод: `PUT`
- URL: `http://127.0.0.1:8000/users/{user_id}`
- Тело запроса (пример):
```json
{
    "first_name": "Иван",
    "last_name": "Петров"
}
```
- Примечание: Все поля опциональны, можно обновить только нужные поля

### 5. Удаление пользователя
- Метод: `DELETE`
- URL: `http://127.0.0.1:8000/users/{user_id}`
- Описание: Удаляет пользователя с указанным ID
- Как использовать: Отправьте DELETE-запрос на URL с ID пользователя

## Структура проекта

```
app_development/
├── app/
│   ├── controller/         # HTTP контроллеры (endpoints)
│   │   └── user_controller.py
│   ├── models/            # SQLAlchemy модели данных
│   │   └── user.py
│   ├── repositories/      # Слой работы с БД
│   │   ├── user_repository.py
│   │   ├── product_repository.py
│   │   └── order_repository.py
│   ├── schemas/           # Pydantic схемы для валидации
│   │   └── user_schema.py
│   ├── services/          # Бизнес-логика
│   │   └── user_service.py
│   ├── providers.py       # Dependency Injection провайдеры
│   └── main.py           # Точка входа приложения
├── models.py                    # Базовые модели данных
├── conftest.py                  # Конфигурация тестов
├── test_user_repository.py      # Тесты репозитория пользователей
├── test_user_endpoints.py       # Тесты эндпоинтов пользователей
├── test_order_repository.py     # Тесты репозитория заказов (edge-cases)
├── test_product_pagination.py   # Тесты пагинации товаров
├── init_db.py                   # Инициализация БД
└── requirements.txt             # Зависимости проекта
```

## Примеры запросов API

### Windows PowerShell:

#### Получение всех пользователей:
```powershell
curl http://127.0.0.1:8000/users
```

#### Создание нового пользователя:
```powershell
$body = @{
    username = "ivan_ivanov"
    email = "ivan@example.com"
    first_name = "Иван"
    last_name = "Иванов"
} | ConvertTo-Json

curl -X POST http://127.0.0.1:8000/users `
     -H "Content-Type: application/json" `
     -d $body
```

#### Обновление пользователя:
```powershell
$body = @{
    first_name = "Иван"
    last_name = "Петров"
} | ConvertTo-Json

curl -X PUT http://127.0.0.1:8000/users/1 `
     -H "Content-Type: application/json" `
     -d $body
```

### Linux/Mac:
```bash
# Создание пользователя
curl -X POST http://127.0.0.1:8000/users \
     -H "Content-Type: application/json" \
     -d '{"username": "ivan_ivanov", "email": "ivan@example.com", "first_name": "Иван", "last_name": "Иванов"}'

# Обновление пользователя
curl -X PUT http://127.0.0.1:8000/users/1 \
     -H "Content-Type: application/json" \
     -d '{"first_name": "Иван", "last_name": "Петров"}'

# Удаление пользователя
curl -X DELETE http://127.0.0.1:8000/users/1
```

## Модели данных

### User (Пользователь)
- `id` - уникальный идентификатор
- `username` - имя пользователя (уникальное)
- `email` - email (уникальный)
- `first_name` - имя
- `last_name` - фамилия

### Product (Продукт)
- `id` - уникальный идентификатор
- `title` - название продукта
- `price_cents` - цена в центах
- `stock_quantity` - количество на складе

### Order (Заказ)
- `id` - уникальный идентификатор
- `user_id` - ID пользователя
- `shipping_address_id` - ID адреса доставки
- `created_at` - дата создания
- `products` - список продуктов в заказе (many-to-many)
```