import pytest
from sqlalchemy import select

from app.models.user import User
from models import Address, Product, Order
from app.schemas.user_schema import UserCreate


@pytest.mark.asyncio
async def test_create_order_with_multiple_products(session, user_repository, product_repository, order_repository):
    # Create user
    user = await user_repository.create(UserCreate(email="u1@example.com", username="u1", first_name="U1", last_name="Test"))

    # Create address via session
    addr = Address(user_id=user.id, city="City", street="Street 1")
    session.add(addr)
    await session.commit()
    await session.refresh(addr)

    # Create products
    p1 = await product_repository.create("Prod A", 1000, 10)
    p2 = await product_repository.create("Prod B", 2000, 5)

    # Create order with both products
    order = await order_repository.create(user.id, addr.id, [p1.id, p2.id])

    assert order is not None
    assert len(order.products) == 2
    ids = {p.id for p in order.products}
    assert ids == {p1.id, p2.id}


@pytest.mark.asyncio
async def test_create_order_with_missing_product_ids(session, user_repository, product_repository, order_repository):
    user = await user_repository.create(UserCreate(email="u2@example.com", username="u2", first_name="U2", last_name="Test"))
    addr = Address(user_id=user.id, city="City", street="Street 2")
    session.add(addr)
    await session.commit()
    await session.refresh(addr)

    p1 = await product_repository.create("Prod C", 500, 3)

    # One valid id and one non-existent id
    order = await order_repository.create(user.id, addr.id, [p1.id, 99999])
    assert order is not None
    assert len(order.products) == 1
    assert order.products[0].id == p1.id


@pytest.mark.asyncio
async def test_create_order_with_duplicate_product_ids(session, user_repository, product_repository, order_repository):
    user = await user_repository.create(UserCreate(email="u3@example.com", username="u3", first_name="U3", last_name="Test"))
    addr = Address(user_id=user.id, city="City", street="Street 3")
    session.add(addr)
    await session.commit()
    await session.refresh(addr)

    p1 = await product_repository.create("Prod D", 1500, 2)

    # Duplicate ids in creation list
    order = await order_repository.create(user.id, addr.id, [p1.id, p1.id])
    assert order is not None
    # Repository should include product only once
    assert len(order.products) == 1
    assert order.products[0].id == p1.id


@pytest.mark.asyncio
async def test_add_product_already_in_order(session, user_repository, product_repository, order_repository):
    user = await user_repository.create(UserCreate(email="u4@example.com", username="u4", first_name="U4", last_name="Test"))
    addr = Address(user_id=user.id, city="City", street="Street 4")
    session.add(addr)
    await session.commit()
    await session.refresh(addr)

    p1 = await product_repository.create("Prod E", 1200, 4)

    order = await order_repository.create(user.id, addr.id, [p1.id])
    # Add same product again
    order = await order_repository.add_product(order.id, p1.id)
    assert len(order.products) == 1


@pytest.mark.asyncio
async def test_remove_product_not_in_order(session, user_repository, product_repository, order_repository):
    user = await user_repository.create(UserCreate(email="u5@example.com", username="u5", first_name="U5", last_name="Test"))
    addr = Address(user_id=user.id, city="City", street="Street 5")
    session.add(addr)
    await session.commit()
    await session.refresh(addr)

    p1 = await product_repository.create("Prod F", 700, 6)
    p2 = await product_repository.create("Prod G", 800, 1)

    order = await order_repository.create(user.id, addr.id, [p1.id])

    # Attempt to remove product not in order (p2)
    order_after = await order_repository.remove_product(order.id, p2.id)
    assert len(order_after.products) == 1
    assert order_after.products[0].id == p1.id


@pytest.mark.asyncio
async def test_create_order_with_empty_products(session, user_repository, order_repository):
    user = await user_repository.create(UserCreate(email="u6@example.com", username="u6", first_name="U6", last_name="Test"))
    addr = Address(user_id=user.id, city="City", street="Street 6")
    session.add(addr)
    await session.commit()
    await session.refresh(addr)

    order = await order_repository.create(user.id, addr.id, [])
    assert order is not None
    assert len(order.products) == 0
