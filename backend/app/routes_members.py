from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel, Field

from .database import get_db
from .models import Member, Team, Membership, User
from .schemas import (
    MemberCreate,
    MemberUpdate,
    MemberResponse,
    MemberListResponse,
    MembershipAssignment,
    MembershipResponse,
    MemberStatusEnum,
)
from .auth import get_current_user, require_admin

router = APIRouter(prefix="/api/members", tags=["members"])


class DesignationUpdate(BaseModel):
    designation: str = Field(min_length=1, max_length=100)


def format_member_response(member: Member) -> MemberResponse:
    memberships_list = [
        MembershipResponse(
            id=ms.id,
            team_id=ms.team_id,
            team_name=ms.team.name if ms.team else None,
            designation=ms.designation,
            joined_at=ms.joined_at,
        )
        for ms in member.memberships
    ]
    return MemberResponse(
        id=member.id,
        user_id=member.user_id,
        full_name=member.full_name,
        email=member.email,
        phone=member.phone,
        department=member.department,
        year=member.year,
        status=MemberStatusEnum(member.status),
        avatar_url=member.avatar_url,
        bio=member.bio,
        date_joined=member.date_joined,
        created_at=member.created_at,
        memberships=memberships_list,
    )


@router.get("", response_model=MemberListResponse)
def list_members(
    search: Optional[str] = Query(None, description="Search by member full name or email"),
    team_id: Optional[int] = Query(None, description="Filter by team ID"),
    designation: Optional[str] = Query(None, description="Filter by designation in a team"),
    department: Optional[str] = Query(None, description="Filter by department"),
    year: Optional[int] = Query(None, ge=1, le=5, description="Filter by year of study"),
    status: Optional[MemberStatusEnum] = Query(None, description="Filter by status (ACTIVE/INACTIVE/ALUMNI)"),
    sort_by: str = Query("name", pattern="^(name|year|date_joined)$", description="Sort by name, year, or date_joined"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order: asc or desc"),
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Member)

    # If filtering by team or designation, join Membership table
    if team_id is not None or designation is not None:
        query = query.join(Membership, Member.id == Membership.member_id)
        if team_id is not None:
            query = query.filter(Membership.team_id == team_id)
        if designation is not None:
            query = query.filter(Membership.designation.ilike(f"%{designation.strip()}%"))

    # Search by full name or email (case-insensitive)
    if search:
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Member.full_name.ilike(search_pattern),
                Member.email.ilike(search_pattern),
            )
        )

    # Filter by department
    if department:
        query = query.filter(Member.department == department)

    # Filter by year
    if year is not None:
        query = query.filter(Member.year == year)

    # Filter by status
    if status is not None:
        query = query.filter(Member.status == status.value)

    # Make query distinct in case of multiple memberships per member
    query = query.distinct()

    total = query.count()

    # Sorting
    sort_column = Member.full_name
    if sort_by == "year":
        sort_column = Member.year
    elif sort_by == "date_joined":
        sort_column = Member.date_joined

    if order == "desc":
        query = query.order_by(sort_column.desc(), Member.id.desc())
    else:
        query = query.order_by(sort_column.asc(), Member.id.asc())

    # Pagination
    offset = (page - 1) * limit
    members = query.offset(offset).limit(limit).all()

    return MemberListResponse(
        total=total,
        page=page,
        limit=limit,
        members=[format_member_response(m) for m in members],
    )


@router.get("/{member_id}", response_model=MemberResponse)
def get_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return format_member_response(member)


@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(
    member_in: MemberCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    # Check duplicate email
    existing = db.query(Member).filter(Member.email == member_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A member with this email already exists",
        )

    # Validate team assignments if provided
    team_assignments = member_in.teams or []
    team_ids = [t.team_id for t in team_assignments]
    if len(team_ids) != len(set(team_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate team assignments found in request",
        )

    for t in team_assignments:
        team_exists = db.query(Team).filter(Team.id == t.team_id).first()
        if not team_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Team with ID {t.team_id} does not exist",
            )

    new_member = Member(
        full_name=member_in.full_name,
        email=member_in.email,
        phone=member_in.phone,
        department=member_in.department,
        year=member_in.year,
        status=member_in.status.value,
        avatar_url=member_in.avatar_url,
        bio=member_in.bio,
        date_joined=member_in.date_joined or date.today(),
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)

    # Add team memberships
    for t in team_assignments:
        membership = Membership(
            member_id=new_member.id,
            team_id=t.team_id,
            designation=t.designation,
        )
        db.add(membership)
    db.commit()
    db.refresh(new_member)

    return format_member_response(new_member)


@router.put("/{member_id}", response_model=MemberResponse)
def update_member(
    member_id: int,
    member_in: MemberUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    if member_in.email is not None and member_in.email != member.email:
        existing = db.query(Member).filter(Member.email == member_in.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A member with this email already exists",
            )
        member.email = member_in.email

    if member_in.full_name is not None:
        member.full_name = member_in.full_name
    if member_in.phone is not None:
        member.phone = member_in.phone
    if member_in.department is not None:
        member.department = member_in.department
    if member_in.year is not None:
        member.year = member_in.year
    if member_in.status is not None:
        member.status = member_in.status.value
    if member_in.avatar_url is not None:
        member.avatar_url = member_in.avatar_url
    if member_in.bio is not None:
        member.bio = member_in.bio
    if member_in.date_joined is not None:
        member.date_joined = member_in.date_joined

    db.commit()
    db.refresh(member)
    return format_member_response(member)


@router.delete("/{member_id}", status_code=status.HTTP_200_OK)
def delete_member(
    member_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    # If this member was leading any teams, set team_lead_id to NULL
    teams_led = db.query(Team).filter(Team.team_lead_id == member_id).all()
    for t in teams_led:
        t.team_lead_id = None

    db.delete(member)
    db.commit()
    return {"message": "Member deleted successfully", "id": member_id}


# --- Team Membership Assignment Sub-Routes ---

@router.post("/{member_id}/teams", response_model=MembershipResponse, status_code=status.HTTP_201_CREATED)
def assign_member_to_team(
    member_id: int,
    assignment: MembershipAssignment,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    team = db.query(Team).filter(Team.id == assignment.team_id).first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    # Check if already assigned
    existing = (
        db.query(Membership)
        .filter(Membership.member_id == member_id, Membership.team_id == assignment.team_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Member is already assigned to this team",
        )

    new_ms = Membership(
        member_id=member_id,
        team_id=assignment.team_id,
        designation=assignment.designation,
    )
    db.add(new_ms)
    db.commit()
    db.refresh(new_ms)

    return MembershipResponse(
        id=new_ms.id,
        team_id=new_ms.team_id,
        team_name=team.name,
        designation=new_ms.designation,
        joined_at=new_ms.joined_at,
    )


@router.put("/{member_id}/teams/{team_id}", response_model=MembershipResponse)
def update_member_team_designation(
    member_id: int,
    team_id: int,
    body: DesignationUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    ms = (
        db.query(Membership)
        .filter(Membership.member_id == member_id, Membership.team_id == team_id)
        .first()
    )
    if not ms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership assignment not found",
        )

    ms.designation = body.designation
    db.commit()
    db.refresh(ms)

    return MembershipResponse(
        id=ms.id,
        team_id=ms.team_id,
        team_name=ms.team.name if ms.team else None,
        designation=ms.designation,
        joined_at=ms.joined_at,
    )


@router.delete("/{member_id}/teams/{team_id}", status_code=status.HTTP_200_OK)
def remove_member_from_team(
    member_id: int,
    team_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    ms = (
        db.query(Membership)
        .filter(Membership.member_id == member_id, Membership.team_id == team_id)
        .first()
    )
    if not ms:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership assignment not found",
        )

    db.delete(ms)
    db.commit()
    return {"message": "Member removed from team successfully"}
