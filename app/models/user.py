from datetime import datetime as date
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserModel(BaseModel):
    id: Optional[str] = None
    name: str
    email: EmailStr
    password: str
    created_at: date = date.now() # timezone do servidor
