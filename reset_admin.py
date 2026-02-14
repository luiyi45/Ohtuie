import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal
from app.core.security import get_password_hash

async def reset_admin():
    new_hash = get_password_hash("admin")
    async with AsyncSessionLocal() as session:
        await session.execute(
            text("UPDATE users SET hashed_password = :hash WHERE email = :email"),
            {"hash": new_hash, "email": "admin@ohtuie.com"}
        )
        await session.commit()
        print(f"Admin password reset successfully. New hash: {new_hash}")

if __name__ == "__main__":
    asyncio.run(reset_admin())
