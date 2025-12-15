import asyncio
from faststream import FastStream
from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from pathlib import Path
import os

from models import Product, Order

broker = RabbitBroker("amqp://guest:guest@rabbitmq:5672/local")
app = FastStream(broker)

# Поддержка переменной окружения для БД (PostgreSQL в Docker, SQLite локально)
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    # Локальный запуск - используем SQLite
    BASE_DIR = Path(__file__).resolve().parent
    DB_PATH = BASE_DIR / "mydb.sqlite3"
    print("DB_PATH =", DB_PATH, "exists:", DB_PATH.exists())  # для проверки работы БД
    DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"
else:
    print(f"Using DATABASE_URL from environment: {DATABASE_URL}")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)



@broker.subscriber("product")
async def subscribe_product(product_data: dict):
    async with async_session() as session:
        product_id = product_data.get("id")
        quantity_in_stock = product_data.get("quantity_in_stock")
        if quantity_in_stock is None:
            print(f"[WARN] В сообщении нет поля 'quantity_in_stock': {product_data}")
            return
        result = await session.execute(
            select(Product).where(Product.id == product_id)
        )
        db_product = result.scalars().first()

        if db_product:
            db_product.title = product_data.get("title", db_product.title)
            db_product.price_cents = product_data.get("price_cents", db_product.price_cents)
            db_product.quantity_in_stock = quantity_in_stock
            print(f"Обновлён продукт {db_product.id}, остаток {db_product.quantity_in_stock}")
        else:
            db_product = Product(
                id=product_id,
                title=product_data.get("title", ""),
                price_cents=product_data.get("price_cents", 0),
                quantity_in_stock=quantity_in_stock,
            )
            session.add(db_product)
            print(f"Создан продукт {db_product.id}, остаток {db_product.quantity_in_stock}")

        await session.commit()


@broker.subscriber("order")
async def subscribe_order(order_data: dict):
    async with async_session() as session:
        product_ids = order_data.get("product_ids", [])

        result = await session.execute(
            select(Product).where(Product.id.in_(product_ids))
        )
        products = result.scalars().all()

        found_ids = {p.id for p in products}
        missing = [pid for pid in product_ids if pid not in found_ids]
        if missing:
            print(f"Заказ отклонён: нет товаров {missing}")
            return

        no_stock = [p.id for p in products if p.quantity_in_stock <= 0]
        if no_stock:
            print(f"Заказ отклонён: товары закончились {no_stock}")
            return

        order = Order(
            user_id=order_data["user_id"],
            shipping_address_id=order_data["shipping_address_id"],
        )
        order.products = products
        session.add(order)

        for p in products:
            p.quantity_in_stock -= 1

        await session.commit()
        print(f"Создан заказ {order.id} с товарами {product_ids}")


async def main():
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())