
import asyncio
import sys
import os
sys.path.append(os.getcwd())
from app.db.session import AsyncSessionLocal
from app import crud, schemas
from app.schemas.user import UserRegistration, UserCreate

async def test_registration_sync():
    async with AsyncSessionLocal() as db:
        test_email = "test_sync@example.com"
        
        # Clean up if exists
        user = await crud.user.get_by_email(db, email=test_email)
        if user:
            from sqlalchemy import text
            await db.execute(text("DELETE FROM cycles WHERE user_id = :uid"), {"uid": user.id})
            await db.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": user.id})
            await db.commit()
            print(f"Cleaned up previous test user: {test_email}")

        # Test registration
        reg_in = UserRegistration(
            user=UserCreate(
                email=test_email,
                password="testpassword",
                full_name="Test Sync User"
            ),
            cycle_duration=25, # Custom value
            period_duration=4, # Custom value
            cycle_start_date="2026-02-01"
        )
        
        # Simulating users.create_user_open logic
        user_in = reg_in.user
        user_in.cycle_duration = reg_in.cycle_duration
        user_in.period_duration = reg_in.period_duration
        
        new_user = await crud.user.create(db, obj_in=user_in)
        print(f"Created user: {new_user.email}")
        print(f"Saved Cycle Duration: {new_user.cycle_duration} (Expected: 25)")
        print(f"Saved Period Duration: {new_user.period_duration} (Expected: 4)")
        
        if new_user.cycle_duration == 25 and new_user.period_duration == 4:
            print("SUCCESS: Data sync is working correctly.")
        else:
            print("FAILURE: Data sync is still broken.")

if __name__ == "__main__":
    asyncio.run(test_registration_sync())
