import asyncio
from app.api import deps
from app.db.session import SessionLocal
from sqlalchemy import select
from app.models.audit_log import AuditLog
from app.models.user import User

async def main():
    async with SessionLocal() as db:
        # Logs
        res = await db.execute(select(AuditLog))
        logs = res.scalars().all()
        print(f"Total Audit Logs: {len(logs)}")
        for log in logs[:10]:
            print(f"  {log.event_type}: {log.description} ({log.created_at})")
            
        # Admin users
        res = await db.execute(select(User).where(User.role == "admin"))
        admins = res.scalars().all()
        print(f"Total Admins: {len(admins)}")
        for admin in admins:
            print(f"  {admin.email}")

if __name__ == "__main__":
    asyncio.run(main())
