import pytest
from app.repositories.product_repository import ProductRepository
from models import Product


class TestProductRepository:
    @pytest.mark.asyncio
    async def test_create_product(self, product_repository: ProductRepository):
        """Тест создания продукта в репозитории"""
        product = await product_repository.create(
            title="Test Product",
            price_cents=1500,
            quantity_in_stock=100
        )

        assert product.id is not None
        assert product.title == "Test Product"
        assert product.price_cents == 1500
        assert product.quantity_in_stock == 100

    @pytest.mark.asyncio
    async def test_get_product_by_id(self, product_repository: ProductRepository):
        """Тест получения продукта по ID"""
        # Создаём продукт
        created_product = await product_repository.create(
            title="Laptop",
            price_cents=50000,
            quantity_in_stock=25
        )

        # Получаем по ID
        found_product = await product_repository.get_by_id(created_product.id)

        assert found_product is not None
        assert found_product.id == created_product.id
        assert found_product.title == "Laptop"
        assert found_product.price_cents == 50000
        assert found_product.quantity_in_stock == 25

    @pytest.mark.asyncio
    async def test_update_product_stock(self, product_repository: ProductRepository):
        """Тест обновления количества товара на складе"""
        # Создаём продукт с начальным остатком
        product = await product_repository.create(
            title="Mouse",
            price_cents=1200,
            quantity_in_stock=50
        )

        # Обновляем количество на складе
        updated_product = await product_repository.update_stock(
            product.id,
            new_quantity=75
        )

        assert updated_product is not None
        assert updated_product.quantity_in_stock == 75
        assert updated_product.title == "Mouse"
        assert updated_product.price_cents == 1200

    @pytest.mark.asyncio
    async def test_get_all_products(self, product_repository: ProductRepository):
        """Тест получения списка всех продуктов"""
        # Создаём несколько продуктов
        await product_repository.create("Product A", 1000, 10)
        await product_repository.create("Product B", 2000, 20)
        await product_repository.create("Product C", 3000, 30)

        # Получаем все продукты
        products = await product_repository.get_all()

        assert len(products) >= 3
        titles = [p.title for p in products]
        assert "Product A" in titles
        assert "Product B" in titles
        assert "Product C" in titles

    @pytest.mark.asyncio
    async def test_delete_product(self, product_repository: ProductRepository):
        """Тест удаления продукта"""
        # Создаём продукт
        product = await product_repository.create(
            title="To Delete Product",
            price_cents=999,
            quantity_in_stock=5
        )

        product_id = product.id

        # Удаляем продукт
        await product_repository.delete(product_id)

        # Проверяем, что продукт удалён
        deleted_product = await product_repository.get_by_id(product_id)
        assert deleted_product is None
