from typing import List, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID

from app.crud.base import CRUDBase
from app.models.daily_log import DailyLog
from app.schemas.daily_log import DailyLogCreate, DailyLogUpdate

class CRUDDailyLog(CRUDBase[DailyLog, DailyLogCreate, DailyLogUpdate]):
    async def get_by_user_and_date(
        self, db: AsyncSession, *, user_id: UUID, date: date
    ) -> Optional[DailyLog]:
        result = await db.execute(
            select(self.model).filter(
                and_(self.model.user_id == user_id, self.model.date == date)
            )
        )
        return result.scalars().first()

    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: DailyLogCreate, user_id: UUID
    ) -> DailyLog:
        db_obj = self.model(
            **obj_in.model_dump(exclude_none=True),
            user_id=user_id,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_multi_by_user(
        self, db: AsyncSession, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[DailyLog]:
        result = await db.execute(
            select(self.model)
            .filter(self.model.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(self.model.date.desc())
        )
        return result.scalars().all()

    async def get_multi_by_user_and_date_range(
        self, db: AsyncSession, *, user_id: UUID, start_date: date, end_date: date
    ) -> List[DailyLog]:
        result = await db.execute(
            select(self.model)
            .filter(
                and_(
                    self.model.user_id == user_id,
                    self.model.date >= start_date,
                    self.model.date <= end_date,
                )
            )
            .order_by(self.model.date.asc())
        )
        return result.scalars().all()

daily_log = CRUDDailyLog(DailyLog)
