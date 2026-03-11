from typing import Any, List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app import crud, models, schemas
from app.api import deps
from app.core import security

router = APIRouter()

@router.get("", response_model=List[schemas.User])
async def read_users(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = await crud.user.get_multi(db, skip=skip, limit=limit)
    # Filter out current user (admin) from the list
    return [u for u in users if u.id != current_user.id]

@router.post("", response_model=schemas.User)
async def create_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional),
) -> Any:
    """
    Create new user.
    Everyone can create their own 'user' account.
    Only superusers can create other accounts with different roles.
    """
    user = await crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    
    # If not an admin, force role to 'user'
    if not current_user or current_user.role != "admin":
        user_in.role = "user"
        
    user = await crud.user.create(db, obj_in=user_in)
    return user

@router.put("/me", response_model=schemas.User)
async def update_user_me(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Update own user profile.
    """
    # 1. Handle last_period_date if provided
    if user_in.last_period_date:
        # Get the most recent cycle
        cycles = await crud.cycle.get_multi_by_user(db, user_id=current_user.id, limit=1)
        if cycles:
            # Update the most recent cycle's start date
            await crud.cycle.update(db, db_obj=cycles[0], obj_in={"start_date": user_in.last_period_date})
        else:
            # Create the first cycle
            cycle_in = schemas.CycleCreate(start_date=user_in.last_period_date, notes="Registro inicial (ajuste)")
            await crud.cycle.create_with_owner(db, obj_in=cycle_in, user_id=current_user.id)

    # 2. Update user profile fields (full_name, email, durations, password)
    user = await crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user

@router.put("/me/password", response_model=schemas.User)
async def update_password_me(
    *,
    db: AsyncSession = Depends(deps.get_db),
    password_in: schemas.UserUpdatePassword,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Update own password.
    """
    if not security.verify_password(password_in.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta")
    
    user_in = schemas.UserUpdate(password=password_in.new_password)
    user = await crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user

@router.post("/me/verify-password", response_model=Any)
async def verify_password_me(
    *,
    db: AsyncSession = Depends(deps.get_db),
    password_in: schemas.UserUpdatePassword = Body(...), # Or a smaller schema, but this works
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Verify current password for the logged in user.
    """
    valid = security.verify_password(password_in.current_password, current_user.hashed_password)
    return {"valid": valid}

@router.get("/me", response_model=schemas.User)
async def read_user_me(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.post("/open", response_model=schemas.User)
async def create_user_open(
    *,
    db: AsyncSession = Depends(deps.get_db),
    reg_in: schemas.UserRegistration,
) -> Any:
    """
    Create new user without needing to be logged in.
    Initializes the user and their first cycle if data is provided.
    """
    user = await crud.user.get_by_email(db, email=reg_in.user.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="El correo ya existe. Recupera tu cuenta",
        )
    
    user_in = reg_in.user
    user_in.role = "user"
    user_in.cycle_duration = reg_in.cycle_duration
    user_in.period_duration = reg_in.period_duration
    user = await crud.user.create(db, obj_in=user_in)
    
    # If cycle data is provided, create the first cycle
    if reg_in.cycle_start_date:
        cycle_in = schemas.CycleCreate(
            start_date=reg_in.cycle_start_date,
            notes="Registro inicial"
        )
        await crud.cycle.create_with_owner(db, obj_in=cycle_in, user_id=user.id)
        
    return user

@router.get("/{user_id}", response_model=schemas.User)
async def read_user_by_id(
    user_id: UUID,
    current_user: models.User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        return user
    if current_user.role != "admin":
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return user

@router.delete("/{user_id}", response_model=schemas.User)
async def delete_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: UUID,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a user.
    """
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Users cannot delete themselves",
        )
    user = await crud.user.remove(db, id=user_id)
    return user

@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: UUID,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    
    # Check if the user is trying to change their own role (optional but good)
    # However, UserUpdate doesn't have role anyway.
    
    user = await crud.user.update(db, db_obj=user, obj_in=user_in)
    return user
