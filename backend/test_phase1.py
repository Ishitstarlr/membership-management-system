import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

from app.database import Base
from app.models import User, Member, Team, Membership
from app.schemas import (
    MemberCreate,
    RoleEnum,
    MemberStatusEnum,
    UserRegister,
)

# Test in-memory / test SQLite engine
TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_models_creation_and_relationships(db_session):
    # 1. Create User
    user = User(email="admin@nitk.edu.in", password_hash="dummy_hash", role=RoleEnum.ADMIN.value)
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
    assert user.role == "ADMIN"

    # 2. Create Member
    member = Member(
        user_id=user.id,
        full_name="Alice Smith",
        email="alice@nitk.edu.in",
        phone="9876543210",
        department="Computer Science",
        year=3,
        status=MemberStatusEnum.ACTIVE.value,
        bio="Web Dev Lead",
    )
    db_session.add(member)
    db_session.commit()
    assert member.id is not None
    assert member.user.email == "admin@nitk.edu.in"

    # 3. Create Team with Member as Lead
    team = Team(
        name="Web Team",
        description="Builds web applications",
        team_lead_id=member.id,
    )
    db_session.add(team)
    db_session.commit()
    assert team.id is not None
    assert team.lead.full_name == "Alice Smith"

    # 4. Create Membership (M:N with designation)
    membership = Membership(
        member_id=member.id,
        team_id=team.id,
        designation="Lead Developer",
    )
    db_session.add(membership)
    db_session.commit()
    assert membership.id is not None
    assert len(member.memberships) == 1
    assert member.memberships[0].designation == "Lead Developer"
    assert len(team.members) == 1


def test_unique_membership_constraint(db_session):
    member = Member(
        full_name="Bob Jones",
        email="bob@nitk.edu.in",
        department="Information Technology",
        year=2,
        status=MemberStatusEnum.ACTIVE.value,
    )
    team = Team(name="AI/ML SIG", description="AI projects")
    db_session.add_all([member, team])
    db_session.commit()

    m1 = Membership(member_id=member.id, team_id=team.id, designation="Core Member")
    db_session.add(m1)
    db_session.commit()

    # Attempt duplicate assignment of same member to same team
    m2 = Membership(member_id=member.id, team_id=team.id, designation="Senior Member")
    db_session.add(m2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_pydantic_schemas_validation():
    # Valid member creation
    valid_data = {
        "full_name": "Carol Danvers",
        "email": "carol@nitk.edu.in",
        "department": "ECE",
        "year": 4,
        "status": "ALUMNI",
    }
    member_schema = MemberCreate(**valid_data)
    assert member_schema.status == MemberStatusEnum.ALUMNI

    # Invalid email
    with pytest.raises(ValidationError):
        MemberCreate(
            full_name="Bad Email",
            email="not-an-email",
            department="CSE",
            year=2,
        )

    # Invalid year (> 5)
    with pytest.raises(ValidationError):
        MemberCreate(
            full_name="Invalid Year",
            email="test@nitk.edu.in",
            department="CSE",
            year=6,
        )

    # User registration schema (no role parameter allowed)
    user_reg = UserRegister(email="student@nitk.edu.in", password="secretpassword")
    assert not hasattr(user_reg, "role") or getattr(user_reg, "role", None) is None
