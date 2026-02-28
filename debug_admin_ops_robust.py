
import asyncio
import sys
import os
import traceback
from uuid import UUID
sys.path.append(os.getcwd())
from app.db.session import AsyncSessionLocal
from app import crud, schemas, models
from app.schemas.user import UserUpdate

async def debug_user_management():
    print("Starting debug script...")
    try:
        async with AsyncSessionLocal() as db:
            # 1. Create a dummy user
            test_email = "to_be_deleted@example.com"
            user = await crud.user.get_by_email(db, email=test_email)
            if not user:
                user_in = schemas.UserCreate(
                    email=test_email,
                    password="testpassword",
                    full_name="Delete Me"
                )
                user = await crud.user.create(db, obj_in=user_in)
                print(f"Created user: {user.email} (ID: {user.id})")
            
            # 2. Add some associated data
            from app.models.cycle import Cycle
            from datetime import date
            from sqlalchemy import text
            await db.execute(text("DELETE FROM cycles WHERE user_id = :uid"), {"uid": user.id})
            await db.commit()
            
            cycle = Cycle(user_id=user.id, start_date=date.today())
            db.add(cycle)
            await db.commit()
            print("Added cycle for user")

            # 3. Try to UPDATE (Block)
            print(f"Attempting to block user {user.id}...")
            update_in = UserUpdate(is_active=False)
            user = await crud.user.get(db, id=user.id)
            updated_user = await crud.user.update(db, db_obj=user, obj_in=update_in)
            print(f"Update SUCCESS: is_active={updated_user.is_active}")

            # 4. Try to DELETE
            print(f"Attempting to delete user {user.id}...")
            user = await crud.user.get(db, id=user.id)
            deleted_user = await crud.user.remove(db, id=user.id)
            if deleted_user:
                print(f"Delete SUCCESS: User {deleted_user.email} removed")
            else:
                print("Delete FAILURE: User not found")
                
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_user_management())
