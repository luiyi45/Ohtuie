import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Hardcoded URL to test
DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/ohtuie"

try:
    print(f"Creating engine with {DATABASE_URL}")
    engine = create_async_engine(DATABASE_URL, echo=True)
    print("Engine created successfully")
except Exception as e:
    print(f"Failed to create engine: {e}")
    import traceback
    traceback.print_exc()
