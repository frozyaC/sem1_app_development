import pika
import json


def send_orders():
    """Отправка заказов в RabbitMQ для создания в БД"""
    # Создание подключения
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="rabbitmq",
            port=5672,
            virtual_host="local",
        )
    )
    channel = connection.channel()

    # Подготовка заказов
    orders = [
        {"user_id": 1, "shipping_address_id": 1, "product_ids": [1, 2]},
        {"user_id": 2, "shipping_address_id": 2, "product_ids": [3, 4]},
        {"user_id": 3, "shipping_address_id": 2, "product_ids": [5]},
    ]

    # Отправка заказов
    for o in orders:
        channel.basic_publish(
            exchange="",
            routing_key="order",
            body=json.dumps(o),
        )
        print(f"Отправлен заказ: user_id={o['user_id']}, товары={o['product_ids']}")

    connection.close()
    print(f"\n✓ Отправлено {len(orders)} заказов в очередь 'order'")


if __name__ == "__main__":
    send_orders()
