from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    password: str
    email: str
    phone: str
    address: str
