from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from .database import get_db
from .models import Member, Team, Membership, User
from .schemas import DashboardStats, NameCount
from .routes_members import format_member_response
from .auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total_members = db.query(func.count(Member.id)).scalar() or 0
    active_count = db.query(func.count(Member.id)).filter(Member.status == "ACTIVE").scalar() or 0
    inactive_count = db.query(func.count(Member.id)).filter(Member.status == "INACTIVE").scalar() or 0
    alumni_count = db.query(func.count(Member.id)).filter(Member.status == "ALUMNI").scalar() or 0
    total_teams = db.query(func.count(Team.id)).scalar() or 0

    # Department distribution
    dept_records = (
        db.query(Member.department, func.count(Member.id))
        .group_by(Member.department)
        .order_by(func.count(Member.id).desc())
        .all()
    )
    department_distribution = [
        NameCount(name=dept or "Unspecified", count=cnt)
        for dept, cnt in dept_records
    ]

    # Year distribution
    year_records = (
        db.query(Member.year, func.count(Member.id))
        .group_by(Member.year)
        .order_by(Member.year.asc())
        .all()
    )
    year_distribution = [
        NameCount(name=f"Year {yr}", count=cnt)
        for yr, cnt in year_records
    ]

    # Team distribution (count members in each team)
    team_records = (
        db.query(Team.name, func.count(Membership.id))
        .outerjoin(Membership, Team.id == Membership.team_id)
        .group_by(Team.id, Team.name)
        .order_by(func.count(Membership.id).desc())
        .all()
    )
    team_distribution = [
        NameCount(name=t_name, count=cnt)
        for t_name, cnt in team_records
    ]

    # Recently added members (up to 5)
    recent = (
        db.query(Member)
        .order_by(Member.created_at.desc(), Member.id.desc())
        .limit(5)
        .all()
    )
    recent_members = [format_member_response(m) for m in recent]

    return DashboardStats(
        total_members=total_members,
        active_count=active_count,
        inactive_count=inactive_count,
        alumni_count=alumni_count,
        total_teams=total_teams,
        department_distribution=department_distribution,
        year_distribution=year_distribution,
        team_distribution=team_distribution,
        recent_members=recent_members,
    )
