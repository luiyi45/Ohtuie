from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.cycle import Cycle
from app.schemas.cycle import CycleCreate, CycleUpdate
from sqlalchemy import extract


class CRUDCycle(CRUDBase[Cycle, CycleCreate, CycleUpdate]):
    async def get_multi_by_user(
        self, db: AsyncSession, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Cycle]:
        result = await db.execute(
            select(Cycle)
            .filter(Cycle.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Cycle.start_date.desc())
        )
        return result.scalars().all()

    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: CycleCreate, user_id: UUID
    ) -> Cycle:
        # Check if a cycle already exists for this user in the same month and year as the new start_date
        result = await db.execute(
            select(Cycle)
            .filter(
                Cycle.user_id == user_id,
                extract('month', Cycle.start_date) == obj_in.start_date.month,
                extract('year', Cycle.start_date) == obj_in.start_date.year
            )
        )
        existing_cycle = result.scalars().first()

        if existing_cycle:
            # If it exists, update it with the new data
            return await self.update(db, db_obj=existing_cycle, obj_in=obj_in)

        # Otherwise, create a new one
        db_obj = Cycle(
            **obj_in.model_dump(),
            user_id=user_id
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove_all_by_user(
        self, db: AsyncSession, *, user_id: UUID
    ) -> int:
        result = await db.execute(
            select(Cycle).filter(Cycle.user_id == user_id)
        )
        objs = result.scalars().all()
        count = len(objs)
        for obj in objs:
            await db.delete(obj)
        await db.commit()
        return count

cycle = CRUDCycle(Cycle)
