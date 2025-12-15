from datetime import date
from taskiq_aio_pika import AioPikaBroker
from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os

from app.models.report import OrderReport
from models import Order, order_products

# Database configuration
# Поддержка как SQLite (локально), так и PostgreSQL (в Docker)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///mydb.sqlite3"
)
engine = create_async_engine(DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# RabbitMQ URL - поддержка локального запуска и Docker
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/local")
broker = AioPikaBroker(
    RABBITMQ_URL,
    exchange_name="report",  # обменник
    queue_name="cmd_order"  # очередь для отправки
)

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)

# Модифицируем задачу, добавив расписание с помощью параметра `schedule`.
# Задача будет выполняться каждую минуту.
@broker.task(
    schedule=[
        {
            "cron": "*/1 * * * *",  # Выражение cron: каждую минуту
            "args": [],  # Без аргументов
            "schedule_id": "create_order_reports",  # Уникальный ID расписания
        }
    ]
)
async def my_scheduled_task() -> str:
    """Задача, выполняемая по расписанию - создание отчётов по заказам."""
    async with async_session_factory() as session:
        # Получаем все заказы
        query = select(Order.id).select_from(Order)
        result = await session.execute(query)
        orders = result.scalars().all()
        
        reports_created = 0
        today = date.today()
        
        for order_id in orders:
            count_query = select(func.count()).select_from(order_products).where(
                order_products.c.order_id == order_id
            )
            count_result = await session.execute(count_query)
            count_product = count_result.scalar() or 0
            
            # Создаём отчёт
            report = OrderReport(
                report_at=today,
                order_id=order_id,
                count_product=count_product
            )
            session.add(report)
            reports_created += 1
        
        await session.commit()
        
        message = f"Created {reports_created} order reports at {today}"
        print(message)
        return message
