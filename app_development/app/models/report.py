from datetime import date
from sqlalchemy import Integer, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

# Use the same Base/metadata as the core models (orders, products, etc.)
# so the FK to orders.id resolves correctly.
from models import Base


class OrderReport(Base):
    __tablename__ = "order_reports"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_at: Mapped[date] = mapped_column(Date, nullable=False)  # день отчёта
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    count_product: Mapped[int] = mapped_column(Integer, nullable=False)  # количество товаров в заказе
