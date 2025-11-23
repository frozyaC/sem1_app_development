import pytest

from app.models.user import User
from app.repositories.user_repository import UserRepository


class TestUserRepository:
    @pytest.mark.asyncio
    async def test_create_user(self, user_repository: UserRepository):
        """Тест создания пользователя в репозитории"""
        user_data = {
            "email": "test@example.com",
            "username": "john_doe",
            "first_name": "John",
            "last_name": "Doe",
        }

        user = await user_repository.create(**user_data)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.username == "john_doe"

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, user_repository: UserRepository):
        """Тест получения пользователя по email"""
        # Сначала создаём пользователя
        user = await user_repository.create(
            email="unique@example.com",
            username="user_test",
            first_name="Test",
            last_name="User",
        )

        # Затем ищем по email
        found_user = await user_repository.get_by_email("unique@example.com")

        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.email == "unique@example.com"

    @pytest.mark.asyncio
    async def test_update_user(self, user_repository: UserRepository):
        """Тест обновления пользователя"""
        user = await user_repository.create(
            email="update@example.com",
            username="test",
            first_name="Original",
            last_name="Name",
        )

        updated_user = await user_repository.update(user.id, first_name="Updated")

        assert updated_user.username == "test"
        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"

    @pytest.mark.asyncio
    async def test_delete_user(self, user_repository: UserRepository):
        """Тест удаления пользователя"""
        user = await user_repository.create(
            email="delete@example.com",
            username="to_delete",
            first_name="Delete",
            last_name="Me",
        )

        user_id = user.id

        # Удаляем пользователя
        await user_repository.delete(user_id)

        # Проверяем, что пользователь удалён
        deleted_user = await user_repository.get_by_id(user_id)
        assert deleted_user is None

    @pytest.mark.asyncio
    async def test_get_all_users(self, user_repository: UserRepository):
        """Тест получения списка всех пользователей"""
        # Создаём несколько пользователей
        await user_repository.create(
            email="user1@example.com",
            username="user1",
            first_name="First",
            last_name="User",
        )
        await user_repository.create(
            email="user2@example.com",
            username="user2",
            first_name="Second",
            last_name="User",
        )
        await user_repository.create(
            email="user3@example.com",
            username="user3",
            first_name="Third",
            last_name="User",
        )

        # Получаем всех пользователей
        users = await user_repository.get_by_filter()

        assert len(users) >= 3
        emails = [u.email for u in users]
        assert "user1@example.com" in emails
        assert "user2@example.com" in emails
        assert "user3@example.com" in emails
