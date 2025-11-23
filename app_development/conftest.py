import pytest
import pytest_asyncio
from litestar.testing import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.user import Base as UserBase
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from models import Base as ModelsBase
from models import Order, Product

# URL тестовой базы данных SQLite с асинхронным драйвером
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def engine():
    """Создаём асинхронный движок SQLAlchemy для подключения к тестовой базе данных"""
    return create_async_engine(TEST_DATABASE_URL, echo=True)


@pytest.fixture(scope="session")
def async_session_factory(engine):
    """Создаём фабрику асинхронных сессий для использования в тестах"""
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session")
async def tables(engine):
    """Создаём и удаляем таблицы в БД на уровне всей сессии тестов"""
    async with engine.begin() as conn:
        # Удаляем все таблицы, если они есть (чистим БД)
        await conn.run_sync(UserBase.metadata.drop_all)
        await conn.run_sync(ModelsBase.metadata.drop_all)
        # Создаём все таблицы по моделям из Base
        await conn.run_sync(UserBase.metadata.create_all)
        await conn.run_sync(ModelsBase.metadata.create_all)
    yield
    # После завершения тестов удаляем созданные таблицы для очистки
    async with engine.begin() as conn:
        await conn.run_sync(UserBase.metadata.drop_all)
        await conn.run_sync(ModelsBase.metadata.drop_all)


@pytest_asyncio.fixture
async def session(engine, tables):
    """Создаём асинхронную сессию для каждого теста"""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        # Очищаем таблицы после каждого теста для изоляции
        await session.execute(UserBase.metadata.tables["users"].delete())
        await session.execute(ModelsBase.metadata.tables["order_products"].delete())
        await session.execute(ModelsBase.metadata.tables["orders"].delete())
        await session.execute(ModelsBase.metadata.tables["products"].delete())
        await session.execute(ModelsBase.metadata.tables["addresses"].delete())
        await session.commit()


@pytest.fixture
def user_repository(session):
    """Фикстура для создания репозитория пользователей с текущей сессией

    UserRepository использует паттерн с установкой session через атрибут,
    поэтому создаём экземпляр и устанавливаем сессию вручную.
    """
    repo = UserRepository()
    repo.session = session
    return repo


@pytest.fixture
def product_repository(session):
    """Фикстура для создания репозитория продуктов с текущей сессией

    ProductRepository принимает сессию через конструктор.
    """
    return ProductRepository(session)


@pytest.fixture
def order_repository(session):
    """Фикстура для создания репозитория заказов с текущей сессией

    OrderRepository принимает сессию через конструктор.
    """
    return OrderRepository(session)


@pytest.fixture
def client(engine, tables):
    """
    Фикстура для тестового клиента Litestar.

    ВАЖНО: Переопределяет зависимости приложения для использования ТЕСТОВОЙ БД!

    Проблема:
    - app из app.main использует реальную БД (mydb.sqlite3)
    - Нужно подменить зависимости на тестовые

    Решение:
    - Создаём тестовую фабрику сессий с engine из фикстуры (test.db)
    - Переопределяем provide_db_session для использования тестовой БД
    - TestClient будет использовать тестовую БД вместо реальной
    """
    from litestar import Litestar
    from litestar.di import Provide
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker

    from app.controller.user_controller import UserController

    # Создаём тестовую фабрику сессий
    test_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Переопределяем provide_db_session для тестов
    async def provide_test_db_session():
        """Провайдер тестовой сессии БД"""
        async with test_session_factory() as session:
            yield session

    # Импортируем классы для типизации
    from app.repositories.user_repository import UserRepository
    from app.services.user_service import UserService

    # Переопределяем provide_user_repository для тестов
    async def provide_test_user_repository(db_session: AsyncSession) -> UserRepository:
        """Провайдер тестового репозитория пользователей"""
        repo = UserRepository()
        repo.session = db_session
        return repo

    # Переопределяем provide_user_service для тестов
    async def provide_test_user_service(user_repository: UserRepository) -> UserService:
        """Провайдер тестового сервиса пользователей"""
        return UserService(user_repository)

    # Создаём тестовое приложение с переопределёнными зависимостями
    test_app = Litestar(
        route_handlers=[UserController],
        dependencies={
            "db_session": Provide(provide_test_db_session),
            "user_repository": Provide(provide_test_user_repository),
            "user_service": Provide(provide_test_user_service),
        },
    )

    return TestClient(app=test_app)
