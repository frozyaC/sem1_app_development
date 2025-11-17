import pytest
from unittest.mock import Mock, AsyncMock
from app.services.order_service import OrderService


class TestOrderService:
    @pytest.mark.asyncio
    async def test_create_order_success(self):
        """Тест успешного создания заказа"""
        # Создаём mock-объекты репозиториев
        mock_order_repo = AsyncMock()
        mock_product_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        # Настраиваем возвращаемые значения
        mock_user_repo.get_by_id.return_value = Mock(
            id=1, name="Test User", email="test@example.com"
        )
        mock_product_repo.get_by_id.return_value = Mock(
            id=1, name="Test Product", price=100.0, quantity_in_stock=5
        )
        mock_order_repo.create.return_value = Mock(
            id=1, user_id=1, total_amount=200.0, status="pending"
        )

        # Создаём экземпляр сервиса
        order_service = OrderService(
            order_repository=mock_order_repo,
            product_repository=mock_product_repo,
            user_repository=mock_user_repo,
        )

        # Данные для создания заказа
        order_data = {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 2}],
        }

        # Вызываем метод
        result = await order_service.create_order(order_data)

        # Проверяем результат
        assert result is not None
        assert result.total_amount == 200.0
        mock_order_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_order_insufficient_stock(self):
        """Тест создания заказа с недостаточным количеством товара"""
        # Создаём mock-объекты репозиториев
        mock_order_repo = AsyncMock()
        mock_product_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        # Настраиваем возвращаемые значения
        mock_user_repo.get_by_id.return_value = Mock(id=1)
        mock_product_repo.get_by_id.return_value = Mock(
            id=1, name="Test Product", price=100.0, quantity_in_stock=1
        )

        # Создаём экземпляр сервиса
        order_service = OrderService(
            order_repository=mock_order_repo,
            product_repository=mock_product_repo,
            user_repository=mock_user_repo,
        )

        # Данные для создания заказа с большим количеством, чем доступно
        order_data = {
            "user_id": 1,
            "items": [{"product_id": 1, "quantity": 5}],  # Запрашиваем больше чем есть
        }

        # Проверяем, что выбрасывается исключение
        with pytest.raises(ValueError, match="Insufficient stock"):
            await order_service.create_order(order_data)

    @pytest.mark.asyncio
    async def test_get_order_by_id(self):
        """Тест получения заказа по ID"""
        # Создаём mock-объекты
        mock_order_repo = AsyncMock()
        mock_product_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        # Настраиваем возвращаемое значение
        mock_order_repo.get_by_id.return_value = Mock(
            id=1, user_id=1, total_amount=200.0
        )

        # Создаём сервис
        order_service = OrderService(
            order_repository=mock_order_repo,
            product_repository=mock_product_repo,
            user_repository=mock_user_repo,
        )

        # Вызываем метод
        result = await order_service.get_order_by_id(1)

        # Проверяем
        assert result is not None
        assert result.id == 1
        mock_order_repo.get_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_all_orders(self):
        """Тест получения всех заказов"""
        # Создаём mock-объекты
        mock_order_repo = AsyncMock()
        mock_product_repo = AsyncMock()
        mock_user_repo = AsyncMock()

        # Настраиваем возвращаемое значение
        mock_order_repo.get_all.return_value = [
            Mock(id=1, user_id=1, total_amount=200.0),
            Mock(id=2, user_id=2, total_amount=300.0),
        ]

        # Создаём сервис
        order_service = OrderService(
            order_repository=mock_order_repo,
            product_repository=mock_product_repo,
            user_repository=mock_user_repo,
        )

        # Вызываем метод
        result = await order_service.get_all_orders()

        # Проверяем
        assert len(result) == 2
        assert result[0].total_amount == 200.0
        assert result[1].total_amount == 300.0
        mock_order_repo.get_all.assert_called_once()
