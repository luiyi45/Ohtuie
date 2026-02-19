import asyncio
import httpx

API_URL = "http://localhost:8000/api/v1"

async def verify_stats():
    async with httpx.AsyncClient() as client:
        # 1. Login as admin
        print("Logging in as admin...")
        login_data = {
            "username": "admin@ohtuie.com",
            "password": "admin123"
        }
        login_res = await client.post(f"{API_URL}/login/access-token", data=login_data)
        if login_res.status_code != 200:
            print(f"Login failed: {login_res.text}")
            return
        
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Get statistics
        print("Fetching admin statistics...")
        stats_res = await client.get(f"{API_URL}/admin/statistics", headers=headers)
        if stats_res.status_code == 200:
            print("Statistics fetched successfully:")
            import json
            print(json.dumps(stats_res.json(), indent=2))
        else:
            print(f"Failed to fetch stats: {stats_res.status_code} - {stats_res.text}")

if __name__ == "__main__":
    asyncio.run(verify_stats())
