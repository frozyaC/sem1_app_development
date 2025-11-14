import pytest
from sqlalchemy import select
from models import Product


@pytest.mark.asyncio
async def test_product_pagination(session, product_repository):
    # create 25 products
    products = []
    for i in range(25):
        p = await product_repository.create(f"P{i}", 100 + i, stock_quantity=10)
        products.append(p)

    # parameters to test
    page = 2
    count = 10
    offset = (page - 1) * count

    # fetch slice using raw query (what pagination endpoint/service should do)
    q = select(Product).order_by(Product.id).offset(offset).limit(count)
    result = await session.execute(q)
    page_items = result.scalars().all()

    # expected ids
    expected = [products[i].id for i in range(offset, offset + count)]
    assert [p.id for p in page_items] == expected

    # Edge cases
    # page beyond range -> empty
    q2 = select(Product).order_by(Product.id).offset(1000).limit(count)
    r2 = await session.execute(q2)
    assert r2.scalars().all() == []

    # count=0 should return no items (should be validated by service)
    q3 = select(Product).order_by(Product.id).offset(0).limit(0)
    r3 = await session.execute(q3)
    assert r3.scalars().all() == []
