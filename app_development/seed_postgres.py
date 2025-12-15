import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Address, Product, Order

# Используем PostgreSQL из переменной окружения или SQLite локально
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///mydb.sqlite3")
# Для seed используем синхронный драйвер
DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

with Session() as session:
    # Пользователи
    user1 = User(name="Anna Ivanova", email="anna@example.com")
    user2 = User(name="Boris Petrov", email="boris@example.com")
    user3 = User(name="Cecilia Smirnova", email="cecilia@example.com")
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
    session.commit()
    
    print(f"✓ Создано {len([user1, user2, user3, user4, user5])} пользователей")
    print(f"✓ Создано {len([addr1, addr2, addr3, addr4, addr5])} адресов")
