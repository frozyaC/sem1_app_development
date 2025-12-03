import pika
import json


def send_message():
    # Создание подключения
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="rabbitmq",
            port=5672,
            virtual_host="local",
        )
    )
    channel = connection.channel()

    # Подготовка сообщения
    products = [
        {"id": 1, "title": "item 1", "price_cents": 1000, "quantity_in_stock": 5},
        {"id": 2, "title": "item 2", "price_cents": 2000, "quantity_in_stock": 3},
        {"id": 3, "title": "item 3", "price_cents": 2500, "quantity_in_stock": 0},
        {"id": 4, "title": "item 4", "price_cents": 2500, "quantity_in_stock": 10},
        {"id": 5, "title": "item 5", "price_cents": 3000, "quantity_in_stock": 1},
    ]

    orders = [
        {"user_id": 1, "shipping_address_id": 1, "product_ids": [1, 2]},
        {"user_id": 2, "shipping_address_id": 2, "product_ids": [3, 4]},
        {"user_id": 3, "shipping_address_id": 2, "product_ids": [5]},
    ]

    # Отправка сообщений
    for p in products:
        channel.basic_publish(
            exchange="",
            routing_key="product",
            body=json.dumps(p),
        )
        print(f"Отправлен продукт {p['id']}")

    for o in orders:
        channel.basic_publish(
            exchange="",
            routing_key="order",
            body=json.dumps(o),
        )
        print(f"Отправлен заказ с товарами {o['product_ids']}")

    connection.close()


if __name__ == "__main__":
    send_message()
