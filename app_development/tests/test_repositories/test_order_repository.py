import pytest

from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from models import Order


class TestOrderRepository:
    @pytest.mark.asyncio
    async def test_create_order_with_multiple_products(
        self,
        order_repository: OrderRepository,
        user_repository: UserRepository,
        product_repository: ProductRepository,
    ):
        """Тест создания заказа с несколькими продуктами"""
        # Создаём пользователя
        user = await user_repository.create(
            email="customer@example.com",
            username="customer",
            first_name="Customer",
            last_name="Name",
        )

        # Создаём несколько продуктов
        product1 = await product_repository.create("Product A", 1000, 50)
        product2 = await product_repository.create("Product B", 2000, 30)
        product3 = await product_repository.create("Product C", 1500, 20)

        # Создаём заказ с несколькими продуктами
        # Примечание: shipping_address_id устанавливаем как 1 для упрощения
        # В реальном проекте нужно создавать Address и использовать его ID
        order = await order_repository.create(
            user_id=user.id,
            shipping_address_id=1,
            product_ids=[product1.id, product2.id, product3.id],
        )

        assert order.id is not None
        assert order.user_id == user.id
        assert len(order.products) == 3

        # Проверяем, что все продукты добавлены
        product_ids = [p.id for p in order.products]
        assert product1.id in product_ids
        assert product2.id in product_ids
        assert product3.id in product_ids

    @pytest.mark.asyncio
    async def test_get_order_by_id(
        self,
        order_repository: OrderRepository,
        user_repository: UserRepository,
        product_repository: ProductRepository,
    ):
        """Тест получения конкретного заказа по ID"""
        # Создаём пользователя и продукты
        user = await user_repository.create(
            email="buyer@example.com",
            username="buyer",
            first_name="Buyer",
            last_name="User",
        )
        product1 = await product_repository.create("Item 1", 500, 10)
        product2 = await product_repository.create("Item 2", 700, 15)

        # Создаём заказ
        created_order = await order_repository.create(
            user_id=user.id,
            shipping_address_id=1,
            product_ids=[product1.id, product2.id],
        )

        # Получаем заказ по ID
        found_order = await order_repository.get_by_id(created_order.id)

        assert found_order is not None
        assert found_order.id == created_order.id
        assert found_order.user_id == user.id
        assert len(found_order.products) == 2

    @pytest.mark.asyncio
    async def test_get_all_orders(
        self,
        order_repository: OrderRepository,
        user_repository: UserRepository,
        product_repository: ProductRepository,
    ):
        """Тест получения списка всех заказов"""
        # Создаём пользователей и продукты
        user1 = await user_repository.create(
            email="user1@example.com",
            username="user1",
            first_name="User",
            last_name="One",
        )
        user2 = await user_repository.create(
            email="user2@example.com",
            username="user2",
            first_name="User",
            last_name="Two",
        )
        product = await product_repository.create("Common Product", 1000, 100)

        # Создаём несколько заказов
        order1 = await order_repository.create(user1.id, 1, [product.id])
        order2 = await order_repository.create(user2.id, 1, [product.id])

        # Получаем все заказы
        orders = await order_repository.get_all()

        assert len(orders) >= 2
        order_ids = [o.id for o in orders]
        assert order1.id in order_ids
        assert order2.id in order_ids

    @pytest.mark.asyncio
    async def test_add_product_to_order(
        self,
        order_repository: OrderRepository,
        user_repository: UserRepository,
        product_repository: ProductRepository,
    ):
        """Тест добавления продукта к существующему заказу (обновление заказа)"""
        # Создаём пользователя и продукты
        user = await user_repository.create(
            email="shopper@example.com",
            username="shopper",
            first_name="Shopper",
            last_name="Name",
        )
        product1 = await product_repository.create("Initial Product", 1000, 10)
        product2 = await product_repository.create("Added Product", 2000, 15)

        # Создаём заказ с одним продуктом
        order = await order_repository.create(
            user_id=user.id, shipping_address_id=1, product_ids=[product1.id]
        )

        assert len(order.products) == 1

        # Добавляем второй продукт к заказу
        updated_order = await order_repository.add_product(order.id, product2.id)

        assert updated_order is not None
        assert len(updated_order.products) == 2

        product_ids = [p.id for p in updated_order.products]
        assert product1.id in product_ids
        assert product2.id in product_ids

    @pytest.mark.asyncio
    async def test_remove_product_from_order(
        self,
        order_repository: OrderRepository,
        user_repository: UserRepository,
        product_repository: ProductRepository,
    ):
        """Тест удаления продукта из заказа (обновление заказа)"""
        # Создаём пользователя и продукты
        user = await user_repository.create(
            email="customer2@example.com",
            username="customer2",
            first_name="Customer",
            last_name="Two",
        )
        product1 = await product_repository.create("Keep Product", 1000, 10)
        product2 = await product_repository.create("Remove Product", 2000, 15)

        # Создаём заказ с двумя продуктами
        order = await order_repository.create(
            user_id=user.id,
            shipping_address_id=1,
            product_ids=[product1.id, product2.id],
        )

        assert len(order.products) == 2

        # Удаляем один продукт из заказа
        updated_order = await order_repository.remove_product(order.id, product2.id)

        assert updated_order is not None
        assert len(updated_order.products) == 1
        assert updated_order.products[0].id == product1.id

    @pytest.mark.asyncio
    async def test_delete_order(
        self,
        order_repository: OrderRepository,
        user_repository: UserRepository,
        product_repository: ProductRepository,
    ):
        """Тест удаления заказа"""
        # Создаём пользователя и продукт
        user = await user_repository.create(
            email="deleter@example.com",
            username="deleter",
            first_name="Delete",
            last_name="Order",
        )
        product = await product_repository.create("Product", 1000, 10)

        # Создаём заказ
        order = await order_repository.create(
            user_id=user.id, shipping_address_id=1, product_ids=[product.id]
        )

        order_id = order.id

        # Удаляем заказ
        await order_repository.delete(order_id)

        # Проверяем, что заказ удалён
        deleted_order = await order_repository.get_by_id(order_id)
        assert deleted_order is None
