import asyncio
from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def check_user(email):
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT email FROM users WHERE email = :email"), {"email": email})
        user = result.first()
        if user:
            print(f"User {email} exists.")
        else:
            print(f"User {email} NOT found.")

if __name__ == "__main__":
    import sys
    email = sys.argv[1] if len(sys.argv) > 1 else "luiyi4455@gmail.com"
    asyncio.run(check_user(email))
