from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Dict, Any

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None

# User schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Station schemas
class StationBase(BaseModel):
    name: str
    mood: str = "Neutral"
    music_preferences: Dict[str, Any] = {}
    voice_config: Dict[str, Any] = {}

class StationCreate(StationBase):
    pass

class StationResponse(StationBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
