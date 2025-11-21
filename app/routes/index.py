from fastapi import APIRouter
from app.routes import contact, company
router = APIRouter()
router.include_router(contact.contact_router, prefix="/contacts", tags=["Contacts"])
router.include_router(company.company_router, prefix="/companies", tags=["Companies"])

