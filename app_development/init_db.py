import asyncio

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = "sqlite:///mydb.sqlite3"


def seed_db():
    """Добавить тестовые данные в БД (таблицы уже созданы миграциями)"""
    engine = create_engine(DATABASE_URL, echo=True)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        from models import User

        # Проверить, есть ли уже тестовый пользователь
        existing = session.query(User).filter(User.email == "test@example.com").first()
        
        if not existing:
            test_user = User(
                name="Test User",
                email="test@example.com",
                decription="Test user description"
            )
            session.add(test_user)
            session.commit()
            print("✓ Test user added")
        else:
            print("✓ Test user already exists")


if __name__ == "__main__":
    seed_db()
    print("Database seeded successfully!")
