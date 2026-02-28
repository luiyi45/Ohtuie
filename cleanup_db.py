
import asyncio
import sys
import os

# Ensure app directory is in path
sys.path.append(os.getcwd())

from sqlalchemy import text
from app.db.session import AsyncSessionLocal

async def cleanup():
    async with AsyncSessionLocal() as session:
        print("Starting database cleanup via app session...")
        
        # 1. Verify admin exists
        try:
            result = await session.execute(text("SELECT id, email FROM users WHERE role = 'admin'"))
            admin = result.fetchone()
            if not admin:
                print("WARNING: No admin user found in 'users' table with role='admin'.")
                # Maybe list roles to see what we have
                res = await session.execute(text("SELECT DISTINCT role FROM users"))
                roles = res.fetchall()
                print(f"Available roles: {[r[0] for r in roles]}")
                return
            else:
                print(f"Admin found: {admin.email} (ID: {admin.id})")
        except Exception as e:
            print(f"Verification failed: {e}")
            return

        # 2. Delete data for non-admin users
        tables = [
            "cycles", 
            "daily_logs", 
            "password_reset_tokens", 
            # "audit_logs" # Removed as it doesn't have user_id
        ]
        
        print("Cleaning related tables...")
        for table in tables:
            try:
                # Use a combined subquery to ensure we only target non-admins
                query = text(f"DELETE FROM {table} WHERE user_id IN (SELECT id FROM users WHERE role != 'admin')")
                result = await session.execute(query)
                await session.commit() # Commit each step to clear transaction state
                print(f"Cleaned {table}: {result.rowcount} rows removed.")
            except Exception as e:
                await session.rollback() # Rollback on error to keep transaction viable
                print(f"Error cleaning {table}: {e}")
        
        # Finally delete the users
        try:
            print("Deleting non-admin users...")
            result = await session.execute(text("DELETE FROM users WHERE role != 'admin'"))
            await session.commit()
            print(f"Deleted {result.rowcount} users successfully.")
        except Exception as e:
            await session.rollback()
            print(f"Error deleting users: {e}")
            import traceback
            traceback.print_exc()
        
        print("Cleanup process ended.")

if __name__ == "__main__":
    asyncio.run(cleanup())
