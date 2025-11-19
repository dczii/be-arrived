from fastapi import APIRouter
from app.routes import contact
router = APIRouter()
router.include_router(contact.contact_router, prefix="/contacts", tags=["Contacts"])

