
import asyncio
import sys
import os
from uuid import UUID
sys.path.append(os.getcwd())
from app.db.session import AsyncSessionLocal
from app import crud, schemas, models
from app.schemas.user import UserUpdate

async def debug_user_management():
    with open("debug_error.txt", "w") as f:
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
                    f.write(f"Created user: {user.email} (ID: {user.id})\n")
                
                # 2. Add some associated data
                from app.models.cycle import Cycle
                from datetime import date
                # Clean existing cycles for this user if any
                from sqlalchemy import text
                await db.execute(text("DELETE FROM cycles WHERE user_id = :uid"), {"uid": user.id})
                await db.commit()
                
                cycle = Cycle(user_id=user.id, start_date=date.today())
                db.add(cycle)
                await db.commit()
                f.write("Added cycle for user\n")

                # 3. Try to UPDATE (Block)
                f.write(f"Attempting to block user {user.id}...\n")
                update_in = UserUpdate(is_active=False)
                # Refresh user to make sure it's in the session correctly
                user = await crud.user.get(db, id=user.id)
                updated_user = await crud.user.update(db, db_obj=user, obj_in=update_in)
                f.write(f"Update SUCCESS: is_active={updated_user.is_active}\n")

                # 4. Try to DELETE
                f.write(f"Attempting to delete user {user.id}...\n")
                # Reload user
                user = await crud.user.get(db, id=user.id)
                deleted_user = await crud.user.remove(db, id=user.id)
                if deleted_user:
                    f.write(f"Delete SUCCESS: User {deleted_user.email} removed\n")
                else:
                    f.write("Delete FAILURE: User not found\n")
        except Exception as e:
            import traceback
            f.write(f"FAILURE: {e}\n")
            f.write(traceback.format_exc())
            print(f"Error occurred, see debug_error.txt")

if __name__ == "__main__":
    asyncio.run(debug_user_management())
