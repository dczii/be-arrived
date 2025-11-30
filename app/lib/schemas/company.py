from pydantic import BaseModel, Field, EmailStr
from typing import Dict, Any

class CompanyBase(BaseModel):
    name: str | None = None
    size: int | None = None
    website: str | None = None
    industry: str | None = None
    monthly_spend: int | None = None
    custom_attributes: Dict[str, Any] | None = None

class CompanyCreate(CompanyBase):
    company_id: str = Field(..., description="The id of your company")
    name: str  = Field(..., description="The name of your company")


class CompanyUpdate(CompanyBase):
    pass
