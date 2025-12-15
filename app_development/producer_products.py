import pika
import json


def send_products():
    """Отправка продуктов в RabbitMQ для создания в БД"""
    # Создание подключения
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="rabbitmq",
            port=5672,
            virtual_host="local",
        )
    )
    channel = connection.channel()

    # Подготовка продуктов
    products = [
        {"id": 1, "title": "item 1", "price_cents": 1000, "quantity_in_stock": 10},
        {"id": 2, "title": "item 2", "price_cents": 2000, "quantity_in_stock": 5},
        {"id": 3, "title": "item 3", "price_cents": 2500, "quantity_in_stock": 10},
        {"id": 4, "title": "item 4", "price_cents": 2500, "quantity_in_stock": 10},
        {"id": 5, "title": "item 5", "price_cents": 3000, "quantity_in_stock": 1},
    ]

    # Отправка продуктов
    for p in products:
        channel.basic_publish(
            exchange="",
            routing_key="product",
            body=json.dumps(p),
        )
        print(f"Отправлен продукт {p['id']}: {p['title']}, остаток {p['quantity_in_stock']}")

    connection.close()
    print(f"\n✓ Отправлено {len(products)} продуктов в очередь 'product'")


if __name__ == "__main__":
    send_products()
