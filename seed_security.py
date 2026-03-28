import asyncio
from datetime import datetime, timedelta
from uuid import uuid4
from app.db.session import SessionLocal
from app.models.audit_log import AuditLog

async def seed():
    async with SessionLocal() as db:
        now = datetime.utcnow()
        
        # 1. Some failed logins in last 24h
        for i in range(5):
            log = AuditLog(
                id=uuid4(),
                event_type="failed_login",
                description=f"Intento fallido para: user{i}@test.com",
                metadata_json={"email": f"user{i}@test.com", "ip": f"192.168.1.{10+i}"},
                created_at=now - timedelta(minutes=10 * i + 5)
            )
            db.add(log)
            
        # 2. Some other security events
        db.add(AuditLog(
            id=uuid4(),
            event_type="user_lockout",
            description="Usuario bloqueado: bad_actor@mail.com",
            metadata_json={"email": "bad_actor@mail.com"},
            created_at=now - timedelta(hours=1)
        ))
        
        db.add(AuditLog(
            id=uuid4(),
            event_type="data_export",
            description="Exportación de datos de usuarias: Admin01",
            metadata_json={"admin": "Admin01"},
            created_at=now - timedelta(hours=3)
        ))

        await db.commit()
        print("Mock security data seeded successfully!")

if __name__ == "__main__":
    try:
        asyncio.run(seed())
    except Exception as e:
        print(f"Error seeding: {e}")
