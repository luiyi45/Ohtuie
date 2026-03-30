import sys
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.api.v1.endpoints.admin import get_statistics
from app.models import User

async def main():
    async with AsyncSessionLocal() as session:
        user = User(id=1, role="admin", is_active=True, is_superuser=True)
        try:
            res = await get_statistics(db=session, current_user=user, f_start="2026-03-23", f_end="2026-03-29", r_start="2026-03-23", r_end="2026-03-29")
            print("OK! Data:", list(res.keys()))
        except Exception as e:
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())
