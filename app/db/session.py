from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Handle missing DATABASE_URL for startup/build resilience
if settings.DATABASE_URL:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        connect_args={
            "statement_cache_size": 0,
            "prepared_statement_cache_size": 0,
        },
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
else:
    engine = None
    AsyncSessionLocal = None

async def get_db():
    if not AsyncSessionLocal:
        raise Exception("DATABASE_URL is not configured. Please set it in your environment variables.")
    async with AsyncSessionLocal() as session:
        yield session
