import asyncio
import argparse
from sqlalchemy import text
from app.db.session import engine

async def run_migration():
    async with engine.begin() as conn:
        print("Adding cycle_duration column...")
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN cycle_duration INTEGER DEFAULT 28;"))
            print("Successfully added cycle_duration.")
        except Exception as e:
            print(f"Error or already exists (cycle_duration): {e}")

        print("Adding period_duration column...")
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN period_duration INTEGER DEFAULT 5;"))
            print("Successfully added period_duration.")
        except Exception as e:
            print(f"Error or already exists (period_duration): {e}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_migration())
