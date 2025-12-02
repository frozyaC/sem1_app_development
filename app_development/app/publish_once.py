import os
import asyncio
from faststream.rabbit import RabbitBroker


async def main() -> None:
    url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/local")
    broker = RabbitBroker(url)
    async with broker:
        await broker.publish("manual-test", "order")
        print("[publish_once] Sent: manual-test -> order")


if __name__ == "__main__":
    asyncio.run(main())
