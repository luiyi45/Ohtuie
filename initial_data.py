import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app.db.session import AsyncSessionLocal
from app import crud, schemas
from app.core import config

async def init_db():
    print(f"Using DATABASE_URL: {config.settings.DATABASE_URL}")
    print("Creating initial data...")
    try:
        async with AsyncSessionLocal() as db:
            admin_email = "admin@ohtuie.com"
            admin_password = "admin" # Change this in production!
            
            user = await crud.user.get_by_email(db, email=admin_email)
            if not user:
                user_in = schemas.UserCreate(
                    email=admin_email,
                    password=admin_password,
                    full_name="System Admin",
                    role="admin",
                    is_active=True,
                )
                user = await crud.user.create(db, obj_in=user_in)
                print(f"Admin user created: {admin_email} / {admin_password}")
            else:
                print(f"Admin user already exists: {admin_email}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(init_db())
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
