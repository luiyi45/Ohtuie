import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.user import User

async def check_admin():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).filter(User.email == "admin@ohtuie.com"))
        user = result.scalars().first()
        if user:
            print(f"User: {user.email}, Is Active: {user.is_active}, Role: {user.role}")
        else:
            print("User not found")

if __name__ == "__main__":
    asyncio.run(check_admin())
