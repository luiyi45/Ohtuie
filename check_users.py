
import asyncio
import sys
import os
sys.path.append(os.getcwd())
from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def check():
    async with AsyncSessionLocal() as s:
        r = await s.execute(text('SELECT email, role FROM users'))
        users = r.fetchall()
        print(f"Total Users: {len(users)}")
        for u in users:
            print(f" - {u[0]} ({u[1]})")

if __name__ == "__main__":
    asyncio.run(check())
