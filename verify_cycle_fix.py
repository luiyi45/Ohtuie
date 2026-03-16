import asyncio
from datetime import date
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.cycle import Cycle
from app.schemas.cycle import CycleCreate
from app.crud.crud_cycle import cycle
from app.db.base import Base

# Test database URL - using aiosqlite which should be in .venv
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

async def test_cycle_duplicate_prevention():
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        user_id = uuid4()
        
        # 1. Create a cycle in a new month (March 2026)
        cycle_in_1 = CycleCreate(
            start_date=date(2026, 3, 1),
            notes="First cycle in March"
        )
        await cycle.create_with_owner(db, obj_in=cycle_in_1, user_id=user_id)
        
        # 2. Check that it was created
        cycles = await cycle.get_multi_by_user(db, user_id=user_id)
        assert len(cycles) == 1
        assert cycles[0].notes == "First cycle in March"
        print("Initial cycle created successfully.")

        # 3. Try to register another cycle in the same month (March 2026)
        cycle_in_2 = CycleCreate(
            start_date=date(2026, 3, 15),
            notes="Updated cycle in March"
        )
        await cycle.create_with_owner(db, obj_in=cycle_in_2, user_id=user_id)

        # 4. Check that it was UPDATED and NOT a new record
        cycles = await cycle.get_multi_by_user(db, user_id=user_id)
        assert len(cycles) == 1
        assert cycles[0].notes == "Updated cycle in March"
        assert cycles[0].start_date == date(2026, 3, 15)
        print("Duplicate prevention verified: existing record updated.")

        # 5. Create a cycle in a DIFFERENT month (April 2026)
        cycle_in_3 = CycleCreate(
            start_date=date(2026, 4, 1),
            notes="Cycle in April"
        )
        await cycle.create_with_owner(db, obj_in=cycle_in_3, user_id=user_id)

        # 6. Check that we now have TWO records
        cycles = await cycle.get_multi_by_user(db, user_id=user_id)
        assert len(cycles) == 2
        print("New month creation verified: separate record created.")

    await engine.dispose()

if __name__ == "__main__":
    try:
        asyncio.run(test_cycle_duplicate_prevention())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
