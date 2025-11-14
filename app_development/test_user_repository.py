import pytest
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate, UserUpdate

class TestUserRepository:
    @pytest.mark.asyncio
    async def test_create_user(self, user_repository: UserRepository):
        """Тест создания пользователя в репозитории"""
        user_data = UserCreate(
            email="test@example.com",
            username="john_doe",
            first_name="John",
            last_name="Doe",
        )
        
        user = await user_repository.create(user_data)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.username == "john_doe"

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, user_repository: UserRepository):
        """Тест получения пользователя по email"""
        # Сначала создаем пользователя
        user = await user_repository.create(
            UserCreate(
                email="unique@example.com",
                username="user_test",
                first_name="Test",
                last_name="User",
            )
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
            UserCreate(
                email="update@example.com",
                username="test",
                first_name="Original",
                last_name="Name",
            )
        )
        
        updated_user = await user_repository.update(
            user.id,
            UserUpdate(first_name="Updated")
        )
        
        assert updated_user.username == "test"
        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"  # не изменилось
