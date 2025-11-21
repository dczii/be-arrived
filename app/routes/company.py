import httpx
from fastapi import APIRouter
from configs import env

url = "https://api.intercom.io/companies"


company_router = APIRouter()

@company_router.get("/") 
async def get_all_companies():
    async with httpx.AsyncClient(headers = {
    "Content-Type": "application/json",
    "Intercom-Version": "2.14",
    "Authorization": f"Bearer {env.intercom_access_token}"
}) as client:
        response = await client.get(url)
        data = response.json()
        return data