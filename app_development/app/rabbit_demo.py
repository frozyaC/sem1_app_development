import os
import asyncio
from faststream import FastStream
from faststream.rabbit import RabbitBroker

RABBIT_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/local")

broker = RabbitBroker(RABBIT_URL)
app = FastStream(broker)


@broker.subscriber("order")
async def handle(msg: str) -> None:
    print(f"[rabbit_demo] Received: {msg}")


@app.after_startup
async def test_publish() -> None:
    # publish a test message to the "order" queue
    await broker.publish("message", "order")


async def main() -> None:
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
