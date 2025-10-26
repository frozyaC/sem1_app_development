from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import *
from datetime import datetime
from db import *


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

with Session() as session:
    # Пользователи
    user1 = User(name="Anna Ivanova", email="anna@example.com")
    user2 = User(name="Boris Petrov", email="boris@example.com")
    user3 = User(name="Cecilia Smirnova", email="cecilia@example.com",)
    user4 = User(name="Dmitry Alexeev", email="dmitry@example.com")
    user5 = User(name="Elena Volkova", email="elena@example.com")

    session.add_all([user1, user2, user3, user4, user5])
    session.flush()  # Чтобы получить user.id для address и orders

    # Адреса
    addr1 = Address(user_id=user1.id, city="Moscow", street="Tverskaya St, 12")
    addr2 = Address(user_id=user2.id, city="Saint Petersburg", street="Nevsky Ave, 45")
    addr3 = Address(user_id=user3.id, city="Kazan", street="Pushkina St, 8")
    addr4 = Address(user_id=user4.id, city="Yekaterinburg", street="Lenina St, 3B")
    addr5 = Address(user_id=user5.id, city="Novosibirsk", street="Krasny Ave, 17")

    session.add_all([addr1, addr2, addr3, addr4, addr5])
    session.flush()

    # Продукты
    product1 = Product(title="Product 1", price_cents=1500)
    product2 = Product(title="Product 2", price_cents=2500)
    product3 = Product(title="Product 3", price_cents=3500)
    product4 = Product(title="Product 4", price_cents=4500)
    product5 = Product(title="Product 5", price_cents=5500)

    session.add_all([product1, product2, product3, product4, product5])
    session.flush()

    # Заказы
    order1 = Order(user_id=user1.id, shipping_address_id=addr1.id, created_at=datetime.now(), products=[product1, product3])
    order2 = Order(user_id=user2.id, shipping_address_id=addr2.id, created_at=datetime.now(), products=[product2])
    order3 = Order(user_id=user3.id, shipping_address_id=addr3.id, created_at=datetime.now(), products=[product1, product4, product5])
    order4 = Order(user_id=user4.id, shipping_address_id=addr4.id, created_at=datetime.now(), products=[product3, product5])
    order5 = Order(user_id=user5.id, shipping_address_id=addr5.id, created_at=datetime.now(), products=[product2, product4])

    session.add_all([order1, order2, order3, order4, order5])

    session.commit()