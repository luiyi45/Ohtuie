from datetime import timedelta, datetime, timezone
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas, models
from app.api import deps
from app.core import security
from app.crud.crud_password_reset import password_reset
from app.services.email import send_password_recovery_email

router = APIRouter()

@router.post("/password-recovery/{email}", response_model=schemas.Msg)
async def recover_password(
    email: str,
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """
    Password recovery
    """
    user = await crud.user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    
    # Rate limit check: max 5 recoveries per 24 hours
    one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
    # Rate limit check: max 20 recoveries per 24 hours (Increased for testing)
    token_count = await password_reset.get_count_by_user_after(db, user_id=user.id, after=one_day_ago)
    if token_count >= 20:
        raise HTTPException(
            status_code=429,
            detail="Too many password recovery requests. Please try again tomorrow.",
        )
    
    # Generate code
    token_obj = await password_reset.create_token(db, user_id=user.id)
    
    # Send email
    email_success = send_password_recovery_email(
        email_to=user.email,
        full_name=user.full_name or "Usuario",
        code=token_obj.code
    )
    
    if not email_success:
        await password_reset.remove_token(db, token_id=token_obj.id)
        raise HTTPException(
            status_code=500,
            detail="Error al enviar el correo de recuperación. Por favor, contacta al soporte o intenta más tarde."
        )
    
    return {"msg": "Recovery code sent."}

@router.post("/reset-password", response_model=schemas.Msg)
async def reset_password(
    body: schemas.PasswordResetConfirm,
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """
    Reset password using code
    """
    user = await password_reset.verify_token(
        db, email=body.email, code=body.code
    )
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired recovery code.",
        )
    
    # Update password
    user_update = schemas.UserUpdate(password=body.new_password)
    await crud.user.update(db, db_obj=user, obj_in=user_update)
    
    return {"msg": "Password updated successfully."}
