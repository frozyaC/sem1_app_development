from datetime import date
from typing import List

from litestar import Controller, get
from litestar.exceptions import HTTPException
from litestar.params import Parameter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.report import OrderReport


class ReportController(Controller):
    path = "/report"

    @get()
    async def get_report_by_date(
        self,
        db_session: AsyncSession,
        report_date: str = Parameter(required=True, description="YYYY-MM-DD"),
    ) -> List[dict]:
        """Возвращает отчеты за указанную дату из таблицы order_reports."""
        try:
            target_date = date.fromisoformat(report_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        query = select(OrderReport).where(OrderReport.report_at == target_date)
        result = await db_session.execute(query)
        reports = result.scalars().all()

        return [
            {
                "id": r.id,
                "report_at": r.report_at.isoformat() if r.report_at else None,
                "order_id": r.order_id,
                "count_product": r.count_product,
            }
            for r in reports
        ]
