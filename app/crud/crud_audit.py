from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog

class CRUDAuditLog:
    async def create(self, db: AsyncSession, *, event_type: str, description: str = None, metadata_json: dict = None) -> AuditLog:
        db_obj = AuditLog(
            event_type=event_type,
            description=description,
            metadata_json=metadata_json
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

audit_log = CRUDAuditLog()
