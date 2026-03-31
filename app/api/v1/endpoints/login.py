from datetime import timedelta, datetime, timezone
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas, models
from app.api import deps
from app.core import security
from app.core.config import settings

router = APIRouter()

@router.post("/login/access-token", response_model=schemas.Token)
async def login_access_token(
    db: AsyncSession = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        user_db = await crud.user.get_by_email(db, email=form_data.username)
        
        # 1. Check if user exists
        if not user_db:
             await crud.audit_log.create(
                db, 
                event_type="failed_login", 
                description=f"Usuario inexistente: {form_data.username}",
                metadata_json={"email": form_data.username}
            )
             raise HTTPException(status_code=400, detail="Incorrect email or password")

        # 2. Authenticate
        user = await crud.user.authenticate(
            db, email=form_data.username, password=form_data.password
        )

        if not user:
            # Check if it was because of lockout
            if user_db.locked_until and user_db.locked_until > datetime.now(timezone.utc):
                await crud.audit_log.create(
                    db, 
                    event_type="user_lockout", 
                    description=f"Usuario bloqueado temporalmente: {form_data.username}",
                    metadata_json={"email": form_data.username, "user_id": str(user_db.id)}
                )
                raise HTTPException(status_code=400, detail="Account is temporarily locked due to multiple failed attempts")
            
            # If not locked but authenticate failed, it's a wrong password
            await crud.audit_log.create(
                db, 
                event_type="failed_login", 
                description=f"Contraseña errónea para usuario: {form_data.username}",
                metadata_json={"email": form_data.username}
            )
            raise HTTPException(status_code=400, detail="Incorrect email or password")
            
        elif not user.is_active:
            await crud.audit_log.create(
                db, 
                event_type="failed_login", 
                description=f"Usuario inactivo intentó ingresar: {form_data.username}",
                metadata_json={"email": form_data.username, "user_id": str(user.id)}
            )
            raise HTTPException(status_code=400, detail="Inactive user")
            
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Log successful login
        await crud.audit_log.create(
            db, 
            event_type="login", 
            description=f"Sesión iniciada: {user.email}",
            metadata_json={"email": user.email, "user_id": str(user.id)}
        )
        
        return {
            "access_token": security.create_access_token(
                user.id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
            "role": user.role,
        }
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

@router.post("/login/check-email", response_model=schemas.Msg)
async def check_email(
    *,
    db: AsyncSession = Depends(deps.get_db),
    email_in: str = Body(..., embed=True)
) -> Any:
    """
    Check if an email exists in the system (for sequential validation).
    """
    user = await crud.user.get_by_email(db, email=email_in)
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Account is temporarily locked")
        
    return {"msg": "Email persists"}

