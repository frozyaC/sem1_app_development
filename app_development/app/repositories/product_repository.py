from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Product
from app.redis_cache import get_redis_cache


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.cache = get_redis_cache()
        self.cache_ttl = 600  # 10 минут в секундах

    def _get_cache_key(self, product_id: int) -> str:
        """Получить ключ кэша для продукта"""
        return f"product:{product_id}"

    def _product_to_dict(self, product: Product) -> dict:
        """Конвертировать Product в dict для кэша"""
        return {
            "id": product.id,
            "title": product.title,
            "price_cents": product.price_cents,
            "quantity_in_stock": product.quantity_in_stock,
        }

    async def get_by_id(self, product_id: int) -> Product | None:
        # Проверяем кэш
        cache_key = self._get_cache_key(product_id)
        cached_data = self.cache.get(cache_key)
        
        if cached_data:
            print(f"[CACHE HIT] Product {product_id} from cache")
            # Воссоздаём объект Product из кэша
            product = Product(**cached_data)
            return product
        
        print(f"[CACHE MISS] Product {product_id} from database")
        # Получаем из БД
        query = select(Product).where(Product.id == product_id)
        result = await self.session.execute(query)
        product = result.scalar_one_or_none()
        
        # Сохраняем в кэш
        if product:
            self.cache.set(cache_key, self._product_to_dict(product), self.cache_ttl)
        
        return product

    async def get_all(self) -> list[Product]:
        query = select(Product)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(
        self, title: str, price_cents: int, quantity_in_stock: int
    ) -> Product:
        product = Product(
            title=title, price_cents=price_cents, quantity_in_stock=quantity_in_stock
        )
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def update_stock(self, product_id: int, new_quantity: int) -> Product | None:
        # Получаем продукт напрямую из БД, минуя кэш
        query = select(Product).where(Product.id == product_id)
        result = await self.session.execute(query)
        product = result.scalar_one_or_none()
        
        if not product:
            return None

        product.quantity_in_stock = new_quantity
        await self.session.commit()
        await self.session.refresh(product)
        
        # Обновляем кэш после изменения
        cache_key = self._get_cache_key(product_id)
        self.cache.set(cache_key, self._product_to_dict(product), self.cache_ttl)
        print(f"[CACHE UPDATE] Product {product_id} updated in cache")
        
        return product

    async def delete(self, product_id: int) -> None:
        # Получаем продукт напрямую из БД, минуя кэш
        query = select(Product).where(Product.id == product_id)
        result = await self.session.execute(query)
        product = result.scalar_one_or_none()
        
        if product:
            await self.session.delete(product)
            await self.session.commit()
            
            # Удаляем из кэша после удаления
            cache_key = self._get_cache_key(product_id)
            self.cache.delete(cache_key)
            print(f"[CACHE DELETE] Product {product_id} removed from cache")
