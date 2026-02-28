
import asyncio
import sys
import os
sys.path.append(os.getcwd())
from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def clear_admin_cycle():
    async with AsyncSessionLocal() as session:
        print("Clearing cycle info for admin...")
        try:
            # Set to NULL
            result = await session.execute(text("UPDATE users SET cycle_duration = NULL, period_duration = NULL WHERE role = 'admin'"))
            await session.commit()
            print(f"Updated {result.rowcount} admin records.")
            
            # Verify
            result = await session.execute(text("SELECT email, cycle_duration, period_duration FROM users WHERE role = 'admin'"))
            admin = result.fetchone()
            print(f"Admin State: {admin}")
        except Exception as e:
            print(f"Error: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(clear_admin_cycle())
