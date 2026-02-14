import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def check_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT email, hashed_password, role FROM users"))
        users = result.all()
        print(f"Total users found: {len(users)}")
        for user in users:
            print(f"Email: {user.email}, Role: {user.role}")
            print(f"Hash: {user.hashed_password}")

if __name__ == "__main__":
    asyncio.run(check_users())
