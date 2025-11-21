from pydantic import BaseModel, EmailStr, Field
from typing import Annotated
from datetime import datetime


# Expand to contact base later for reuse
class ContactBase(BaseModel):
    name: str = Field(
        ..., min_length=2, max_length=50, json_schema_extra={"example": "jaylord"}
    )
    email: EmailStr = Field(..., json_schema_extra={"example": "jaylord@example.com"})
    phone: str = Field(
        ..., json_schema_extra={"example": "+639090909090"}
    )  # no pattern for now


class ContactCreate(ContactBase):
    role: str = Field(..., json_schema_extra={"example": "Lead"})

class ContactUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=50)
    email: EmailStr | None = None
    phone: str | None = None

