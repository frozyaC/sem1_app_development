# API Управления Пользователями

Это REST API приложение, построенное с использованием Litestar и SQLAlchemy для управления пользователями.

## Установка и Настройка

1. Создание и активация виртуального окружения:
```bash
python -m venv venv
.\venv\Scripts\activate  # для Windows
source venv/bin/activate  # для Linux/Mac
```

2. Установка зависимостей:
```bash
# Основные зависимости
pip install -r requirements.txt

# Или через pyproject.toml с dev-зависимостями
pip install -e ".[dev]"
```

3. Инициализация базы данных:
```bash
# Создание таблиц базы данных
python init_db.py
```

4. Запуск приложения:
```bash
python -m app.main
```

Сервер запустится по адресу `http://127.0.0.1:8000`

## Тестирование

Подробная информация о тестах находится в [tests/README.md](tests/README.md).

### Быстрый старт:
```bash
# Все тесты
pytest

# Только unit-тесты
pytest tests/test_repositories/ tests/test_services/

# Только API тесты
pytest tests/test_routes/

# С покрытием кода
pytest --cov=app --cov-report=html

# Параллельный запуск
pytest -n auto
```

Всего тестов: **26** (16 repository + 4 service + 6 API)

## Примеры использования API

В папке `crud_examples` находятся примеры Python-скриптов для каждой CRUD операции:

1. `get_operations.py` - примеры получения данных:
   - Получение списка всех пользователей
   - Получение конкретного пользователя по ID
   ```bash
   python crud_examples/get_operations.py
   ```

2. `post_operations.py` - примеры создания новых пользователей:
   - Создание нового пользователя
   - Обработка ошибок при дублировании данных
   ```bash
   python crud_examples/post_operations.py
   ```

3. `put_operations.py` - примеры обновления данных:
   - Полное обновление пользователя
   - Частичное обновление отдельных полей
   ```bash
   python crud_examples/put_operations.py
   ```

4. `delete_operations.py` - примеры удаления данных:
   - Удаление пользователя
   - Проверка успешного удаления
   ```bash
   python crud_examples/delete_operations.py
   ```

Каждый файл содержит подробные комментарии и примеры использования. Перед запуском примеров убедитесь, что:
1. Сервер запущен (`python -m app.main`)
2. База данных инициализирована (`python init_db.py`)
3. Установлен пакет requests (`pip install requests`)

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
    "full_name": "Иван Иванов"
}
```
- Как использовать: Отправьте POST-запрос с JSON-данными (можно использовать Postman или curl)

### 4. Обновление пользователя
- Метод: `PUT`
- URL: `http://127.0.0.1:8000/users/{user_id}`
- Тело запроса (пример):
```json
{
    "username": "ivan_updated",
    "email": "ivan.new@example.com",
    "full_name": "Иван Иванов Обновленный"
}
```
- Как использовать: Отправьте PUT-запрос с JSON-данными для обновления пользователя с указанным ID

### 5. Удаление пользователя
- Метод: `DELETE`
- URL: `http://127.0.0.1:8000/users/{user_id}`
- Описание: Удаляет пользователя с указанным ID
- Как использовать: Отправьте DELETE-запрос на URL с ID пользователя

## Как тестировать API

1. Использование CURL (в командной строке Windows PowerShell):

### Получение всех пользователей:
```powershell
curl http://127.0.0.1:8000/users
```

### Получение конкретного пользователя (например, с ID=1):
```powershell
curl http://127.0.0.1:8000/users/1
```

### Создание нового пользователя:
```powershell
$body = @{
    username = "ivan_ivanov"
    email = "ivan@example.com"
    full_name = "Иван Иванов"
} | ConvertTo-Json

curl -X POST http://127.0.0.1:8000/users `
     -H "Content-Type: application/json" `
     -d $body
```

### Обновление пользователя (например, с ID=1):
```powershell
$body = @{
    username = "ivan_updated"
    email = "ivan.new@example.com"
    full_name = "Иван Иванов Обновленный"
} | ConvertTo-Json

curl -X PUT http://127.0.0.1:8000/users/1 `
     -H "Content-Type: application/json" `
     -d $body
```

### Удаление пользователя (например, с ID=1):
```powershell
curl -X DELETE http://127.0.0.1:8000/users/1
```

Для командной строки Linux/Mac используйте обратный слэш (\) вместо backtick (`) для переноса строк:
```bash
curl -X POST http://127.0.0.1:8000/users \
     -H "Content-Type: application/json" \
     -d '{"username": "ivan_ivanov", "email": "ivan@example.com", "full_name": "Иван Иванов"}'
```

2. Используя Postman:
- Установите Postman (https://www.postman.com/downloads/)
- Создайте новый запрос, выберите метод (GET, POST, PUT, DELETE)
- Введите URL
- Для POST и PUT запросов добавьте тело запроса во вкладке "Body" в формате JSON
- Нажмите "Send"

3. Используя браузер:
- GET запросы можно выполнять прямо в браузере, просто введя URL
- Для остальных методов нужно использовать специальные инструменты (Postman, curl или расширения браузера)
```