"""
Интеграционные тесты для эндпоинтов пользователей.
Используют polyfactory для генерации тестовых данных и create_test_client для тестирования HTTP-эндпоинтов.

Фикстура client из conftest.py настроена для использования изолированной тестовой базы данных (test.db),
что обеспечивает независимость тестов от production-данных.
"""
from typing import Protocol, runtime_checkable

import pytest
from litestar import get
from litestar.di import Provide
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED
from litestar.testing import create_test_client
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel

from app.models.user import User
from app.schemas.user_schema import UserCreate, UserResponse


# Модель для тестирования
class Item(BaseModel):
    """Простая модель Item для демонстрации паттерна тестирования"""

    name: str


# Протокол для сервиса (добавлен @runtime_checkable для проверки типов во время выполнения)
@runtime_checkable
class Service(Protocol):
    """Протокол определяет интерфейс сервиса для dependency injection"""

    def get_one(self) -> Item:
        """Получить один элемент"""
        ...


# Эндпоинт для получения Item
@get(path="/item")
def get_item(service: Service) -> Item:
    """
    Эндпоинт возвращает Item, полученный из сервиса.
    Использует dependency injection для получения сервиса.
    """
    return service.get_one()


# Фабрика для генерации тестовых данных Item
class ItemFactory(ModelFactory[Item]):
    """
    Фабрика для создания тестовых объектов Item.
    Использует polyfactory для автоматической генерации данных.
    """

    __model__ = Item


# Фикстура для создания тестового Item
@pytest.fixture()
def item():
    """
    Фикстура создаёт тестовый Item с помощью фабрики.
    Используется в тестах для получения готового объекта.
    """
    return ItemFactory.build()


def test_get_item(item: Item):
    """
    Тест проверяет эндпоинт получения Item.

    Шаги:
    1. Создаётся mock-сервис с методом get_one(), возвращающим тестовый item
    2. Создаётся тестовый клиент с route_handlers и dependencies
    3. Выполняется GET-запрос к эндпоинту
    4. Проверяется статус-код ответа
    5. Проверяется, что JSON-ответ соответствует модели item
    """

    # Создаём внутренний класс MyService, реализующий протокол Service
    class MyService(Service):
        def get_one(self) -> Item:
            # Возвращаем тестовый item из фикстуры
            return item

    # Создаём тестовый клиент с настроенными маршрутами и зависимостями
    with create_test_client(
        route_handlers=[get_item],  # Регистрируем обработчик эндпоинта
        dependencies={"service": Provide(lambda: MyService())},  # Внедряем mock-сервис
    ) as client:
        # Выполняем GET-запрос к эндпоинту
        response = client.get("/item")

        # Проверяем успешный статус-код
        assert response.status_code == HTTP_200_OK
        # Проверяем, что JSON-ответ соответствует модели item
        assert response.json() == item.model_dump()


# ==================== ТЕСТЫ ДЛЯ USER ENDPOINTS ====================


class TestUserEndpoints:
    """
    Интеграционные тесты для эндпоинтов пользователей.
    Используют изолированную тестовую базу данных через фикстуру client.
    """

    def test_create_user_endpoint(self, client):
        """
        Тест создания нового пользователя через HTTP-эндпоинт.

        Проверяет:
        - POST-запрос к эндпоинту /users
        - Корректность создания пользователя
        - Возврат данных созданного пользователя
        """
        # Данные для создания пользователя
        user_data = {
            "username": "endpoint_user",
            "email": "endpoint@example.com",
            "full_name": "Endpoint User",
        }

        # Выполняем POST-запрос к эндпоинту
        response = client.post("/users", json=user_data)

        # Проверяем статус-код создания (Litestar по умолчанию возвращает 201)
        assert response.status_code in [HTTP_200_OK, HTTP_201_CREATED]

        # Проверяем данные в ответе
        data = response.json()
        assert data["email"] == "endpoint@example.com"
        assert data["username"] == "endpoint_user"
        assert "id" in data

    def test_get_user_by_id_endpoint(self, client):
        """
        Тест получения пользователя по ID через HTTP-эндпоинт.

        Проверяет:
        - Создание пользователя
        - GET-запрос к эндпоинту /users/{id}
        - Корректность возвращаемых данных
        """
        # Сначала создаём пользователя
        user_data = {
            "username": "getbyid_user",
            "email": "getbyid@example.com",
            "full_name": "Get By Id User",
        }
        create_response = client.post("/users", json=user_data)
        created_user = create_response.json()
        user_id = created_user["id"]

        # Выполняем GET-запрос к эндпоинту
        response = client.get(f"/users/{user_id}")

        # Проверяем успешный статус-код
        assert response.status_code == HTTP_200_OK

        # Проверяем данные в ответе
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == "getbyid@example.com"
        assert data["username"] == "getbyid_user"

    def test_get_all_users_endpoint(self, client):
        """
        Тест получения списка всех пользователей через HTTP-эндпоинт.

        Проверяет:
        - GET-запрос к эндпоинту /users
        - Возврат списка пользователей
        - Пагинацию
        """
        # Создаём несколько пользователей
        for i in range(3):
            user_data = {
                "username": f"listuser{i}",
                "email": f"listuser{i}@example.com",
                "full_name": f"List User {i}",
            }
            client.post("/users", json=user_data)

        # Выполняем GET-запрос к эндпоинту
        response = client.get("/users?count=10&page=1")

        # Проверяем успешный статус-код
        assert response.status_code == HTTP_200_OK

        # Проверяем, что вернулся список
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_update_user_endpoint(self, client):
        """
        Тест обновления пользователя через HTTP-эндпоинт.

        Проверяет:
        - Создание пользователя
        - PUT-запрос к эндпоинту /users/{id}
        - Корректность обновления данных
        """
        # Создаём пользователя
        user_data = {
            "username": "update_user",
            "email": "update@example.com",
            "full_name": "Update User",
        }
        create_response = client.post("/users", json=user_data)
        created_user = create_response.json()
        user_id = created_user["id"]

        # Обновляем пользователя
        update_data = {"full_name": "Updated Name"}
        response = client.put(f"/users/{user_id}", json=update_data)

        # Проверяем успешный статус-код
        assert response.status_code == HTTP_200_OK

        # Проверяем обновлённые данные
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["username"] == "update_user"  # Не изменилось

    def test_delete_user_endpoint(self, client):
        """
        Тест удаления пользователя через HTTP-эндпоинт.

        Проверяет:
        - Создание пользователя
        - DELETE-запрос к эндпоинту /users/{id}
        - Проверка, что пользователь удалён
        """
        # Создаём пользователя
        user_data = {
            "username": "delete_user",
            "email": "delete@example.com",
            "full_name": "Delete User",
        }
        create_response = client.post("/users", json=user_data)
        created_user = create_response.json()
        user_id = created_user["id"]

        # Удаляем пользователя
        response = client.delete(f"/users/{user_id}")

        # Проверяем успешный статус-код (обычно 204 или 200)
        assert response.status_code in [HTTP_200_OK, 204]

        # Проверяем, что пользователь действительно удалён
        get_response = client.get(f"/users/{user_id}")
        assert get_response.status_code == 404  # Not Found
