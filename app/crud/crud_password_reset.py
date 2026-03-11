from datetime import datetime, timedelta, timezone
import random
import string
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.password_reset import PasswordResetToken
from app.models.user import User

class CRUDPasswordReset:
    async def get_count_by_user_after(self, db: AsyncSession, *, user_id: str, after: datetime) -> int:
        from sqlalchemy import func
        query = select(func.count(PasswordResetToken.id)).filter(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.created_at >= after
        )
        result = await db.execute(query)
        return result.scalar() or 0

    async def cleanup_tokens(self, db: AsyncSession) -> None:
        from sqlalchemy import delete
        # Delete tokens older than 24 hours
        one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
        query = delete(PasswordResetToken).where(
            PasswordResetToken.created_at < one_day_ago
        )
        await db.execute(query)
        await db.commit()

    async def create_token(self, db: AsyncSession, *, user_id: str) -> PasswordResetToken:
        # Periodic cleanup
        await self.cleanup_tokens(db)
        
        code = "".join(random.choices(string.digits, k=6))
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        db_obj = PasswordResetToken(
            user_id=user_id,
            code=code,
            expires_at=expires_at
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def verify_token(self, db: AsyncSession, *, email: str, code: str) -> Optional[User]:
        # Join with User to verify email
        query = select(PasswordResetToken).join(User).filter(
            User.email == email,
            PasswordResetToken.code == code,
            PasswordResetToken.is_used == False,
            PasswordResetToken.expires_at > datetime.now(timezone.utc)
        )
        result = await db.execute(query)
        token = result.scalars().first()
        
        if token:
            # Mark token as used
            token.is_used = True
            await db.commit()
            
            # Fetch user
            user_result = await db.execute(select(User).filter(User.id == token.user_id))
            return user_result.scalars().first()
        return None

    async def remove_token(self, db: AsyncSession, *, token_id: str) -> None:
        from sqlalchemy import delete
        query = delete(PasswordResetToken).where(PasswordResetToken.id == token_id)
        await db.execute(query)
        await db.commit()


password_reset = CRUDPasswordReset()
