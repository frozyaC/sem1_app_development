# Тесты проекта

Этот проект содержит комплексный набор тестов для проверки работоспособности приложения на основе Litestar.

## Структура тестов

```
tests/
├── conftest.py                    # Общие фикстуры для всех тестов
├── test_repositories/             # Unit-тесты репозиториев
│   ├── __init__.py
│   ├── test_user_repository.py    # 5 тестов
│   ├── test_product_repository.py # 5 тестов
│   └── test_order_repository.py   # 6 тестов
├── test_services/                 # Mock-тесты сервисов
│   ├── __init__.py
│   └── test_order_service.py      # 4 теста
└── test_routes/                   # Интеграционные тесты API
    ├── __init__.py
    └── test_user_endpoints.py     # 6 тестов
```

### 1. Repository Tests (test_repositories/)
Тестируют слой доступа к данным (Data Access Layer).

**Особенности:**
- Используют изолированную тестовую БД (`test.db`)
- База очищается после каждого теста
- Проверяют CRUD-операции (Create, Read, Update, Delete)
- Используют реальную базу данных через SQLAlchemy

### 2. Service Tests (test_services/)
Тестируют бизнес-логику с использованием mock-объектов.

**Особенности:**
- Используют `AsyncMock` для изоляции от БД
- Тестируют валидацию данных и бизнес-правила
- Не требуют реальной БД
- Быстрые и независимые

### 3. API Routes Tests (test_routes/)
Тестируют HTTP-эндпоинты приложения.

**Особенности:**
- Используют `TestClient` от Litestar
- Тестируют полный стек: HTTP → Controller → Service → Repository → Database
- Используют изолированную тестовую БД через dependency injection
- Проверяют статус-коды, структуру ответов, работу CRUD-операций

## Зависимости

Тесты требуют следующие библиотеки (указаны в `pyproject.toml`):
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.0.0",
    "pytest-xdist>=3.0.0",
    "polyfactory>=2.0.0",
]
```

Установка зависимостей для разработки:
```bash
pip install -e ".[dev]"
```

Или через requirements.txt:
```bash
pip install -r requirements.txt
```

## Запуск тестов

### Все тесты:
```bash
pytest
```

### Только unit-тесты (repositories + services):
```bash
pytest tests/test_repositories/ tests/test_services/
```

### Только тесты репозиториев:
```bash
pytest tests/test_repositories/
```

### Только тесты сервисов:
```bash
pytest tests/test_services/
```

### Только API тесты:
```bash
pytest tests/test_routes/
```

### С покрытием кода:
```bash
pytest --cov=app --cov-report=html
```

После выполнения откройте `htmlcov/index.html` для просмотра отчёта.

### Параллельный запуск (требует pytest-xdist):
```bash
pytest -n auto
```

### Конкретный файл:
```bash
pytest tests/test_repositories/test_user_repository.py -v
```

### Конкретный класс тестов:
```bash
pytest tests/test_routes/test_user_endpoints.py::TestUserEndpoints -v
```

### Конкретный тест:
```bash
pytest tests/test_repositories/test_user_repository.py::TestUserRepository::test_create_user -v
```

### С выводом print-сообщений:
```bash
pytest -v -s
```

### С кратким traceback:
```bash
pytest -v --tb=short
```

### С подробным выводом для упавших тестов:
```bash
pytest -v --tb=long
```

## Конфигурация тестов

Основная конфигурация находится в корневом `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = "--verbose --color=yes"
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

### Фикстуры (conftest.py)

#### Для repository-тестов:
- `engine` - движок SQLAlchemy для тестовой БД
- `tables` - создание/очистка таблиц
- `session` - сессия БД с автоматическим rollback
- `user_repository`, `product_repository`, `order_repository` - репозитории

#### Для endpoint-тестов:
- `client` - TestClient с переопределёнными зависимостями для использования тестовой БД

## Изоляция тестов

Все тесты используют изолированную тестовую БД (`test.db`) вместо production БД (`mydb.sqlite3`):

1. **Repository-тесты**: используют фикстуру `session`, которая очищает БД после каждого теста
2. **Endpoint-тесты**: используют фикстуру `client`, которая переопределяет dependency injection для использования тестовой БД

## Покрытие функциональности

### UserRepository (5 тестов):
- ✅ Создание пользователя
- ✅ Получение пользователя по email
- ✅ Обновление данных пользователя
- ✅ Удаление пользователя
- ✅ Получение списка всех пользователей

### ProductRepository (5 тестов):
- ✅ Создание продукта
- ✅ Получение продукта по ID
- ✅ Обновление остатков на складе
- ✅ Получение всех продуктов
- ✅ Удаление продукта

### OrderRepository (6 тестов):
- ✅ Создание заказа с несколькими продуктами
- ✅ Получение заказа по ID
- ✅ Получение всех заказов
- ✅ Добавление продукта в заказ
- ✅ Удаление продукта из заказа
- ✅ Удаление заказа

### OrderService (4 mock-теста):
- ✅ Создание заказа (успешный сценарий)
- ✅ Создание заказа (недостаточно товара на складе)
- ✅ Получение заказа по ID
- ✅ Получение всех заказов

### User Endpoints (6 интеграционных тестов):
- ✅ Демонстрационный тест с Protocol
- ✅ POST /users - создание пользователя
- ✅ GET /users/{id} - получение пользователя
- ✅ GET /users - получение списка пользователей
- ✅ PUT /users/{id} - обновление пользователя
- ✅ DELETE /users/{id} - удаление пользователя

## Примеры использования

### Пример repository-теста:
```python
async def test_create_user(self, user_repository, session):
    user = User(username="testuser", email="test@example.com")
    created_user = await user_repository.create(user)
    assert created_user.id is not None
    assert created_user.username == "testuser"
```

### Пример mock-теста:
```python
async def test_create_order_success(self, order_service, ...):
    mock_user_repo.get_by_id.return_value = mock_user
    mock_product_repo.get_by_id.return_value = mock_product
    
    result = await order_service.create_order(...)
    assert result.id == 1
```

### Пример endpoint-теста:
```python
def test_create_user_endpoint(self, client):
    response = client.post("/users", json={"username": "test", ...})
    assert response.status_code in [200, 201]
    assert response.json()["username"] == "test"
```

## Полезные команды

### Запуск только быстрых тестов (mock):
```bash
pytest tests/test_services/ -v
```

### Запуск только интеграционных тестов:
```bash
pytest tests/test_routes/ -v
```

### Запуск unit-тестов (repositories + services):
```bash
pytest tests/test_repositories/ tests/test_services/ -v
```

### Запуск с подробным выводом SQL-запросов:
Раскомментируйте `echo=True` в `conftest.py` в создании engine

### Проверка покрытия кода с HTML-отчётом:
```bash
pytest --cov=app --cov-report=html
# Откройте htmlcov/index.html в браузере
```

### Проверка покрытия с выводом в терминал:
```bash
pytest --cov=app --cov-report=term-missing
```

### Параллельный запуск для ускорения:
```bash
# Автоматическое определение количества процессов
pytest -n auto

# Или явно указать количество процессов
pytest -n 4
```

## Troubleshooting

### Проблема: тесты падают с ошибкой "table has no column"
**Решение:** Убедитесь, что используется правильная модель Base. В `conftest.py` импортируются обе модели: `UserBase` и `ModelsBase`.

### Проблема: тесты эндпоинтов используют production БД
**Решение:** Фикстура `client` в `conftest.py` должна переопределять зависимости через `Provide()`.

### Проблема: тесты не изолированы, влияют друг на друга
**Решение:** Проверьте, что фикстура `session` правильно выполняет rollback после каждого теста.

## Статистика

**Всего тестов:** 26  
**Repository тесты:** 16  
**Mock тесты:** 4  
**Endpoint тесты:** 6  

**Статус:** ✅ Все тесты проходят успешно
