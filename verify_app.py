import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.getcwd())

try:
    from app.core.config import settings
    import os
    with open("debug_env.txt", "w") as f:
        f.write(f"OS ENV DATABASE_URL: {os.environ.get('DATABASE_URL')}\n")
        f.write(f"SETTINGS DATABASE_URL: {settings.DATABASE_URL}\n")
    from app.main import app
    print("Application imported successfully.")
except Exception as e:
    with open("debug_error.txt", "w") as f:
        f.write(f"Error: {e}\n")
        import traceback
        traceback.print_exc(file=f)
    sys.exit(1)

print("Verification complete.")
