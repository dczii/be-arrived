from pydantic import BaseModel, EmailStr, Field

# Expand to contact base later for reuse
class ContactCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, example="jaylord")
    email: EmailStr = Field(..., example="jaylord@example.com")
    phone: str = Field(..., example="+639090909090") #no pattern for now
    role: str = Field(..., example="Lead")
