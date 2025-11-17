from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from models import Order


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        user_repository: UserRepository
    ):
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.user_repository = user_repository

    async def create_order(self, order_data: dict) -> Order:
        """Создание заказа с проверкой наличия товара на складе"""
        user_id = order_data.get("user_id")
        items = order_data.get("items", [])
        
        # Проверяем существование пользователя
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Проверяем наличие товаров и их количество на складе
        product_ids = []
        for item in items:
            product_id = item["product_id"]
            quantity = item["quantity"]
            
            product = await self.product_repository.get_by_id(product_id)
            if not product:
                raise ValueError(f"Product with id {product_id} not found")
            
            if product.quantity_in_stock < quantity:
                raise ValueError("Insufficient stock")
            
            product_ids.append(product_id)
        
        # Создаём заказ
        order = await self.order_repository.create(
            user_id=user_id,
            shipping_address_id=order_data.get("shipping_address_id", 1),
            product_ids=product_ids
        )
        
        return order

    async def get_order_by_id(self, order_id: int) -> Order | None:
        """Получение заказа по ID"""
        return await self.order_repository.get_by_id(order_id)

    async def get_all_orders(self) -> list[Order]:
        """Получение всех заказов"""
        return await self.order_repository.get_all()
