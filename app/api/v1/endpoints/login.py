from datetime import timedelta, datetime
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
        user = await crud.user.authenticate(
            db, email=form_data.username, password=form_data.password
        )
        if not user:
            await crud.audit_log.create(
                db, 
                event_type="failed_login", 
                description=f"Login fallido para el email: {form_data.username}",
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

