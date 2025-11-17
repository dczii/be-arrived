import httpx
from fastapi import APIRouter
from app.configs import env
import json

contact_router = APIRouter()

#simple request for now
@contact_router.get("/list_all_contacts")
async def get_all_contacts():
    async with httpx.AsyncClient(headers={
        "Intercom-Version": "2.14",
        "Authorization": f"Bearer {env.intercom_access_token}"}
        ) as client:
        url = "https://api.intercom.io/contacts"

        response = await client.get(url)
        return response.json()