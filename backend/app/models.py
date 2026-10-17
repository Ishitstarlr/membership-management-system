from datetime import datetime, date, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from .database import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="MEMBER", nullable=False)  # "ADMIN" or "MEMBER"
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    member_profile = relationship("Member", back_populates="user", uselist=False)


class Member(Base):
    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), unique=True, nullable=True)
    full_name = Column(String(150), index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(30), nullable=True)
    department = Column(String(100), index=True, nullable=False)
    year = Column(Integer, index=True, nullable=False)  # 1, 2, 3, 4, 5
    status = Column(String(20), default="ACTIVE", index=True, nullable=False)  # "ACTIVE", "INACTIVE", "ALUMNI"
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    date_joined = Column(Date, default=date.today, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    user = relationship("User", back_populates="member_profile")
    memberships = relationship(
        "Membership",
        back_populates="member",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    team_lead_id = Column(Integer, ForeignKey("members.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    lead = relationship("Member", foreign_keys=[team_lead_id])
    members = relationship(
        "Membership",
        back_populates="team",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Membership(Base):
    __tablename__ = "memberships"

    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    designation = Column(String(100), nullable=False)  # e.g., "Lead", "Core", "Executive", "Member"
    joined_at = Column(Date, default=date.today, nullable=False)

    member = relationship("Member", back_populates="memberships")
    team = relationship("Team", back_populates="members")

    __table_args__ = (
        UniqueConstraint("member_id", "team_id", name="uq_member_team"),
    )
