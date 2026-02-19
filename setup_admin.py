import asyncio
from sqlalchemy import text, select
from app.db.session import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User

async def setup_admin():
    async with AsyncSessionLocal() as session:
        # Check if admin exists
        result = await session.execute(select(User).where(User.email == "admin@ohtuie.com"))
        admin = result.scalar_one_of_none()
        
        if admin:
            print("Admin user found. Updating role to 'admin' and ensuring password.")
            new_hash = get_password_hash("admin123")
            await session.execute(
                text("UPDATE users SET role = 'admin', hashed_password = :hash, is_active = True WHERE email = :email"),
                {"hash": new_hash, "email": "admin@ohtuie.com"}
            )
        else:
            print("Admin user not found. Creating new admin user.")
            new_hash = get_password_hash("admin123")
            await session.execute(
                text("INSERT INTO users (email, hashed_password, full_name, role, is_active) VALUES (:email, :hash, 'Administrator', 'admin', True)"),
                {"email": "admin@ohtuie.com", "hash": new_hash}
            )
        
        await session.commit()
    print("Admin setup complete. Email: admin@ohtuie.com, Password: admin123")

if __name__ == "__main__":
    asyncio.run(setup_admin())
