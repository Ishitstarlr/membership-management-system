from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from .database import get_db
from .models import Team, Member, Membership, User
from .schemas import (
    TeamCreate,
    TeamUpdate,
    TeamResponse,
    TeamDetailResponse,
    TeamRosterMember,
)
from .auth import get_current_user, require_admin

router = APIRouter(prefix="/api/teams", tags=["teams"])


def format_team_response(team: Team, db: Session) -> TeamResponse:
    member_count = db.query(func.count(Membership.id)).filter(Membership.team_id == team.id).scalar() or 0
    lead_name = team.lead.full_name if team.lead else None
    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        team_lead_id=team.team_lead_id,
        team_lead_name=lead_name,
        member_count=member_count,
        created_at=team.created_at,
    )


@router.get("", response_model=List[TeamResponse])
def list_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    teams = db.query(Team).order_by(Team.name.asc()).all()
    return [format_team_response(team, db) for team in teams]


@router.get("/{team_id}", response_model=TeamDetailResponse)
def get_team_detail(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    base = format_team_response(team, db)
    
    # Build roster
    roster_records = (
        db.query(Membership, Member)
        .join(Member, Membership.member_id == Member.id)
        .filter(Membership.team_id == team.id)
        .order_by(Member.full_name.asc())
        .all()
    )

    roster = [
        TeamRosterMember(
            member_id=mem.id,
            full_name=mem.full_name,
            email=mem.email,
            designation=ms.designation,
            status=mem.status,
            avatar_url=mem.avatar_url,
        )
        for ms, mem in roster_records
    ]

    return TeamDetailResponse(
        **base.model_dump(),
        roster=roster,
    )


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    team_in: TeamCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    existing = db.query(Team).filter(Team.name == team_in.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A team with this name already exists",
        )

    if team_in.team_lead_id is not None:
        lead = db.query(Member).filter(Member.id == team_in.team_lead_id).first()
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned team lead does not exist in members",
            )

    new_team = Team(
        name=team_in.name,
        description=team_in.description,
        team_lead_id=team_in.team_lead_id,
    )
    db.add(new_team)
    db.commit()
    db.refresh(new_team)

    # If lead is assigned, ensure lead is also in memberships with designation 'Lead' if not already
    if new_team.team_lead_id:
        existing_ms = (
            db.query(Membership)
            .filter(Membership.member_id == new_team.team_lead_id, Membership.team_id == new_team.id)
            .first()
        )
        if not existing_ms:
            lead_ms = Membership(
                member_id=new_team.team_lead_id,
                team_id=new_team.id,
                designation="Lead",
            )
            db.add(lead_ms)
            db.commit()

    return format_team_response(new_team, db)


@router.put("/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: int,
    team_in: TeamUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    if team_in.name is not None and team_in.name != team.name:
        existing = db.query(Team).filter(Team.name == team_in.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A team with this name already exists",
            )
        team.name = team_in.name

    if team_in.description is not None:
        team.description = team_in.description

    if team_in.team_lead_id is not None:
        if team_in.team_lead_id != team.team_lead_id:
            lead = db.query(Member).filter(Member.id == team_in.team_lead_id).first()
            if not lead:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Assigned team lead does not exist in members",
                )
            team.team_lead_id = team_in.team_lead_id
            # Also ensure membership
            existing_ms = (
                db.query(Membership)
                .filter(Membership.member_id == team.team_lead_id, Membership.team_id == team.id)
                .first()
            )
            if not existing_ms:
                lead_ms = Membership(
                    member_id=team.team_lead_id,
                    team_id=team.id,
                    designation="Lead",
                )
                db.add(lead_ms)

    db.commit()
    db.refresh(team)
    return format_team_response(team, db)


@router.delete("/{team_id}", status_code=status.HTTP_200_OK)
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    db.delete(team)
    db.commit()
    return {"message": "Team deleted successfully", "id": team_id}
