# # models.py
# from sqlalchemy import Column, Integer, String, ForeignKey
# from sqlalchemy.orm import declarative_base, relationship
# from sqlalchemy import DateTime, func, Table

# Base = declarative_base()

# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True)
#     name = Column(String(100), nullable=False)
#     email = Column(String(255), unique=True, nullable=False)
#     decription = Column(String(200))

#     addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")

# class Address(Base):
#     __tablename__ = "addresses"
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     city = Column(String(100), nullable=False)
#     street = Column(String(200), nullable=False)

#     user = relationship("User", back_populates="addresses")

# order_products = Table(
#     "order_products",
#     Base.metadata,
#     Column("order_id", ForeignKey("orders.id"), primary_key=True),
#     Column("product_id", ForeignKey("products.id"), primary_key=True),
# )

# class Product(Base):
#     __tablename__ = "products"
#     id = Column(Integer, primary_key=True)
#     title = Column(String(200), nullable=False)
#     price_cents = Column(Integer, nullable=False)

# class Order(Base):
#     __tablename__ = "orders"
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
#     shipping_address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
#     created_at = Column(DateTime, server_default=func.now(), nullable=False)

#     user = relationship("User")
#     shipping_address = relationship("Address")
#     products = relationship("Product", secondary=order_products, lazy="selectin")

from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

order_products = Table(
    "order_products",
    Base.metadata,
    Column("order_id", ForeignKey("orders.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    decription = Column(String(200))

    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")

class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    city = Column(String(100), nullable=False)
    street = Column(String(200), nullable=False)

    user = relationship("User", back_populates="addresses")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    price_cents = Column(Integer, nullable=False)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shipping_address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User")
    shipping_address = relationship("Address")
    products = relationship("Product", secondary=order_products, lazy="selectin")
