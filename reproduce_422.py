import asyncio
from datetime import date
from pydantic import ValidationError
from app.schemas.daily_log import DailyLogCreate

async def test_reproduction():
    payload = {
        'date': '2026-02-21',
        'flow': 'none',
        'symptoms': ['Crampings', 'Hinchazón'],
        'moods': ['Feliz'],
    }
    
    try:
        log_in = DailyLogCreate(**payload)
        print("Validation successful:")
        print(log_in.model_dump())
    except ValidationError as e:
        print("Validation failed:")
        for error in e.errors():
            print(f"Field: {error['loc']}, Message: {error['msg']}, Type: {error['type']}")

if __name__ == "__main__":
    asyncio.run(test_reproduction())
