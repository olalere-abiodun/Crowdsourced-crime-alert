from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from enum import Enum
from datetime import datetime

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserBase(BaseModel):
    user_id: int
    username: str
    email: EmailStr


class UserCreate(UserBase):
    fullname: str
    password: str
    role: UserRole


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    user_id: int
    fullname: str
    username: str
    email: EmailStr
    role: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: Optional[str] = None
    fullname: Optional[str] = None
    old_password: Optional[str] = None
    new_password: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)



class CrimeBase(BaseModel):
    crime_type: str
    description: str
    latitude: float
    longitude: float
    media_url: Optional[str] = None


class CrimeCreate(CrimeBase):
    pass


class CrimeResponse(CrimeBase):
    crime_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CrimeUpdate(BaseModel):
    crime_type: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    media_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class VoteBase(BaseModel):
    crime_id: int
    vote_type: str


class VoteCreate(VoteBase):
    pass


class VoteResponse(VoteBase):
    vote_id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubscriptionBase(BaseModel):
    latitude: float
    longitude: float
    radius: float
    is_active: Optional[bool] = True


class SubscriptionCreate(SubscriptionBase):
    pass


class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)