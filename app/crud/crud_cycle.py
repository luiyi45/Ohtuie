from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.cycle import Cycle
from app.schemas.cycle import CycleCreate, CycleUpdate

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
        db_obj = Cycle(
            **obj_in.model_dump(),
            user_id=user_id
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

cycle = CRUDCycle(Cycle)
