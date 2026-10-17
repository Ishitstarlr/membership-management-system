from datetime import datetime, date
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RoleEnum(str, Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class MemberStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ALUMNI = "ALUMNI"


# --- User & Auth Schemas ---
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, description="Password must be at least 6 characters")
    # Note: Public registration NEVER allows choosing role; always defaults to MEMBER.


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    role: RoleEnum
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: RoleEnum
    email: EmailStr
    user_id: int


# --- Membership Schemas ---
class MembershipAssignment(BaseModel):
    team_id: int
    designation: str = Field(min_length=1, max_length=100)


class MembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    team_id: int
    team_name: Optional[str] = None
    designation: str
    joined_at: date


# --- Member Schemas ---
class MemberBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=30)
    department: str = Field(min_length=2, max_length=100)
    year: int = Field(ge=1, le=5)
    status: MemberStatusEnum = MemberStatusEnum.ACTIVE
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    date_joined: Optional[date] = None


class MemberCreate(MemberBase):
    teams: Optional[List[MembershipAssignment]] = []


class MemberUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    year: Optional[int] = Field(default=None, ge=1, le=5)
    status: Optional[MemberStatusEnum] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    date_joined: Optional[date] = None


class MemberResponse(MemberBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    date_joined: date
    created_at: datetime
    memberships: List[MembershipResponse] = []


class MemberListResponse(BaseModel):
    total: int
    page: int
    limit: int
    members: List[MemberResponse]


# --- Team Schemas ---
class TeamBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: Optional[str] = None
    team_lead_id: Optional[int] = None


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    description: Optional[str] = None
    team_lead_id: Optional[int] = None


class TeamRosterMember(BaseModel):
    member_id: int
    full_name: str
    email: str
    designation: str
    status: str
    avatar_url: Optional[str] = None


class TeamResponse(TeamBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    team_lead_name: Optional[str] = None
    member_count: int = 0


class TeamDetailResponse(TeamResponse):
    roster: List[TeamRosterMember] = []


# --- Dashboard Schemas ---
class NameCount(BaseModel):
    name: str
    count: int


class DashboardStats(BaseModel):
    total_members: int
    active_count: int
    inactive_count: int
    alumni_count: int
    total_teams: int
    department_distribution: List[NameCount]
    year_distribution: List[NameCount]
    team_distribution: List[NameCount]
    recent_members: List[MemberResponse]
