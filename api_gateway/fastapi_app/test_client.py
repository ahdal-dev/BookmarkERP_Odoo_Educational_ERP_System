import asyncio
from main import app
from httpx import AsyncClient

async def test():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/registrar/dashboard")
        print(response.status_code)
        print(response.text)

asyncio.run(test())
