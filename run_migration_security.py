import asyncio
from sqlalchemy import text
from app.db.session import engine

async def run_migration():
    async with engine.begin() as conn:
        print("Adding failed_login_attempts column...")
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0;"))
            print("Successfully added failed_login_attempts.")
        except Exception as e:
            print(f"Error or already exists (failed_login_attempts): {e}")

        print("Adding locked_until column...")
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN locked_until TIMESTAMP WITH TIME ZONE;"))
            print("Successfully added locked_until.")
        except Exception as e:
            print(f"Error or already exists (locked_until): {e}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_migration())
