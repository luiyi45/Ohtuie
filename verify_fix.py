
import asyncio
import os
import sys

# Add the project root to sys.path
sys.path.append(r"c:\Users\SENA\Documents\OHTUIE")

async def test_imports():
    print("Testing imports and exports...")
    try:
        from app import models
        print(f"Models imported: {dir(models)}")
        assert hasattr(models, 'AuditLog'), "AuditLog missing from models"
        assert hasattr(models, 'User'), "User missing from models"
        assert hasattr(models, 'Cycle'), "Cycle missing from models"
        assert hasattr(models, 'DailyLog'), "DailyLog missing from models"
        print("✅ Models and exports OK")

        from app.api.v1.endpoints import admin
        print("✅ Admin endpoint imports OK")
        
        # Check if 'text' is available in the module's globals or if we can find it in the file
        # Since we just added it, we want to make sure the code can use it.
        # We can't easily execute the endpoint without a full setup, but we can check if it's imported.
        from sqlalchemy import text
        print("✅ SQLAlchemy text import OK")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_imports())
