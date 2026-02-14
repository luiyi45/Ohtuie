from datetime import datetime, timedelta
import random
import string
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.password_reset import PasswordResetToken
from app.models.user import User

class CRUDPasswordReset:
    async def create_token(self, db: AsyncSession, *, user_id: str) -> PasswordResetToken:
        code = "".join(random.choices(string.digits, k=6))
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        
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
            PasswordResetToken.expires_at > datetime.utcnow()
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

password_reset = CRUDPasswordReset()
