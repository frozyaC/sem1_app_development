from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Order, Product


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, order_id: int) -> Order | None:
        query = select(Order).options(selectinload(Order.products)).where(Order.id == order_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Order]:
        query = select(Order).options(selectinload(Order.products))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_user(self, user_id: int) -> list[Order]:
        query = select(Order).options(selectinload(Order.products)).where(Order.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, user_id: int, shipping_address_id: int, product_ids: list[int]) -> Order:
        order = Order(
            user_id=user_id,
            shipping_address_id=shipping_address_id
        )
        
        # Добавляем продукты к заказу
        if product_ids:
            query = select(Product).where(Product.id.in_(product_ids))
            result = await self.session.execute(query)
            products = list(result.scalars().all())
            order.products.extend(products)
        
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def add_product(self, order_id: int, product_id: int) -> Order | None:
        order = await self.get_by_id(order_id)
        if not order:
            return None
        
        query = select(Product).where(Product.id == product_id)
        result = await self.session.execute(query)
        product = result.scalar_one_or_none()
        
        if product and product not in order.products:
            order.products.append(product)
            await self.session.commit()
            await self.session.refresh(order)
        
        return order

    async def remove_product(self, order_id: int, product_id: int) -> Order | None:
        order = await self.get_by_id(order_id)
        if not order:
            return None
        
        query = select(Product).where(Product.id == product_id)
        result = await self.session.execute(query)
        product = result.scalar_one_or_none()
        
        if product and product in order.products:
            order.products.remove(product)
            await self.session.commit()
            await self.session.refresh(order)
        
        return order

    async def delete(self, order_id: int) -> None:
        order = await self.get_by_id(order_id)
        if order:
            await self.session.delete(order)
            await self.session.commit()
