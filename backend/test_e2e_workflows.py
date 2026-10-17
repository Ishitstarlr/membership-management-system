import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import User, Member, Team, Membership
from app.auth import hash_password

TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def e2e_client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_complete_e2e_lifecycle(e2e_client, db_session):
    # -------------------------------------------------------------
    # 1. Registration & Login (Security: Always MEMBER)
    # -------------------------------------------------------------
    reg_res = e2e_client.post("/api/auth/register", json={
        "email": "student@nitk.edu.in",
        "password": "strongPassword123"
    })
    assert reg_res.status_code == 201
    reg_user = reg_res.json()
    assert reg_user["role"] == "MEMBER"

    # Login with newly registered user
    login_res = e2e_client.post("/api/auth/login", json={
        "email": "student@nitk.edu.in",
        "password": "strongPassword123"
    })
    assert login_res.status_code == 200
    member_token = login_res.json()["access_token"]
    member_headers = {"Authorization": f"Bearer {member_token}"}

    # Create admin user safely in database
    admin_user = User(email="admin@nitk.edu.in", password_hash=hash_password("adminSecret123"), role="ADMIN")
    db_session.add(admin_user)
    db_session.commit()

    admin_login = e2e_client.post("/api/auth/login", json={
        "email": "admin@nitk.edu.in",
        "password": "adminSecret123"
    })
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # -------------------------------------------------------------
    # 2. Team Creation, Editing, Rosters & Rejection of Unauthorized Actions
    # -------------------------------------------------------------
    # Regular member tries to create team -> 403 Forbidden
    unauth_team = e2e_client.post("/api/teams", json={"name": "Hacking Team"}, headers=member_headers)
    assert unauth_team.status_code == 403

    # Admin creates Web Development Team
    team1_res = e2e_client.post("/api/teams", json={
        "name": "Web Development",
        "description": "ACM NITK Web Engineering"
    }, headers=admin_headers)
    assert team1_res.status_code == 201
    team1 = team1_res.json()

    # Admin creates AI/ML SIG
    team2_res = e2e_client.post("/api/teams", json={
        "name": "AI/ML SIG",
        "description": "Machine Learning Research"
    }, headers=admin_headers)
    assert team2_res.status_code == 201
    team2 = team2_res.json()

    # -------------------------------------------------------------
    # 3. Member Creation with Multiple Teams & Distinct Designations
    # -------------------------------------------------------------
    # Regular member tries to create member -> 403 Forbidden
    unauth_mem = e2e_client.post("/api/members", json={
        "full_name": "Unauthorized User",
        "email": "unauth@nitk.edu.in",
        "department": "CSE",
        "year": 2,
    }, headers=member_headers)
    assert unauth_mem.status_code == 403

    # Admin creates Member 1 (assigned to Web Dev as Lead, and AI/ML as Core)
    mem1_res = e2e_client.post("/api/members", json={
        "full_name": "Pooja Hegde",
        "email": "pooja.hegde@nitk.edu.in",
        "department": "Information Technology",
        "year": 3,
        "status": "ACTIVE",
        "teams": [
            {"team_id": team1["id"], "designation": "Team Lead"},
            {"team_id": team2["id"], "designation": "Core Researcher"}
        ]
    }, headers=admin_headers)
    assert mem1_res.status_code == 201
    mem1 = mem1_res.json()
    assert len(mem1["memberships"]) == 2

    # Admin assigns Pooja as Team Lead of Web Dev
    up_t1 = e2e_client.put(f"/api/teams/{team1['id']}", json={"team_lead_id": mem1["id"]}, headers=admin_headers)
    assert up_t1.status_code == 200
    assert up_t1.json()["team_lead_name"] == "Pooja Hegde"

    # Admin creates Member 2 (INACTIVE, Year 1, CSE)
    mem2_res = e2e_client.post("/api/members", json={
        "full_name": "Rohan Deshmukh",
        "email": "rohan.deshmukh@nitk.edu.in",
        "department": "Computer Science & Engineering",
        "year": 1,
        "status": "INACTIVE",
    }, headers=admin_headers)
    assert mem2_res.status_code == 201
    mem2 = mem2_res.json()

    # Admin creates Member 3 (ALUMNI, Year 4, ECE)
    mem3_res = e2e_client.post("/api/members", json={
        "full_name": "Divya Pai",
        "email": "divya.pai@nitk.edu.in",
        "department": "Electronics & Communication",
        "year": 4,
        "status": "ALUMNI",
    }, headers=admin_headers)
    assert mem3_res.status_code == 201

    # -------------------------------------------------------------
    # 4. Multi-Team Assignment Sub-routes
    # -------------------------------------------------------------
    # Assign Rohan to Web Development as Mentee
    assign_res = e2e_client.post(f"/api/members/{mem2['id']}/teams", json={
        "team_id": team1["id"],
        "designation": "Mentee"
    }, headers=admin_headers)
    assert assign_res.status_code == 201

    # Verify Team 1 roster shows both Pooja and Rohan with their designations
    t1_roster = e2e_client.get(f"/api/teams/{team1['id']}", headers=member_headers).json()
    assert t1_roster["member_count"] == 2
    roster_names = [m["full_name"] for m in t1_roster["roster"]]
    assert "Pooja Hegde" in roster_names
    assert "Rohan Deshmukh" in roster_names

    # Update Rohan's designation in Web Dev to "Junior Developer"
    up_desig = e2e_client.put(f"/api/members/{mem2['id']}/teams/{team1['id']}", json={
        "designation": "Junior Developer"
    }, headers=admin_headers)
    assert up_desig.status_code == 200
    assert up_desig.json()["designation"] == "Junior Developer"

    # -------------------------------------------------------------
    # 5. Search, Simultaneous Multi-Filtering, Sorting & Pagination
    # -------------------------------------------------------------
    # Search by partial name
    s1 = e2e_client.get("/api/members?search=pooja", headers=member_headers).json()
    assert s1["total"] == 1
    assert s1["members"][0]["full_name"] == "Pooja Hegde"

    # Search by partial email
    s2 = e2e_client.get("/api/members?search=rohan.deshmukh", headers=member_headers).json()
    assert s2["total"] == 1

    # Multi-Filter: CSE + Year 1 + INACTIVE
    mf = e2e_client.get(
        "/api/members",
        params={
            "department": "Computer Science & Engineering",
            "year": 1,
            "status": "INACTIVE",
        },
        headers=member_headers,
    ).json()
    assert mf["total"] == 1
    assert mf["members"][0]["full_name"] == "Rohan Deshmukh"

    # Filter by Team 1
    tf = e2e_client.get(f"/api/members?team_id={team1['id']}", headers=member_headers).json()
    assert tf["total"] == 2

    # Sorting by year descending
    sort_res = e2e_client.get("/api/members?sort_by=year&order=desc", headers=member_headers).json()
    years = [m["year"] for m in sort_res["members"]]
    assert years == [4, 3, 1]

    # Pagination: limit 2
    p1 = e2e_client.get("/api/members?limit=2&page=1", headers=member_headers).json()
    assert len(p1["members"]) == 2
    assert p1["total"] == 3

    p2 = e2e_client.get("/api/members?limit=2&page=2", headers=member_headers).json()
    assert len(p2["members"]) == 1

    # -------------------------------------------------------------
    # 6. Dashboard Live Calculations
    # -------------------------------------------------------------
    dash = e2e_client.get("/api/dashboard/stats", headers=member_headers).json()
    assert dash["total_members"] == 3
    assert dash["active_count"] == 1
    assert dash["inactive_count"] == 1
    assert dash["alumni_count"] == 1
    assert dash["total_teams"] == 2
    assert len(dash["recent_members"]) == 3

    # -------------------------------------------------------------
    # 7. Member Editing & Deletion Cascades
    # -------------------------------------------------------------
    # Update Pooja's status to INACTIVE
    up_m = e2e_client.put(f"/api/members/{mem1['id']}", json={"status": "INACTIVE"}, headers=admin_headers)
    assert up_m.status_code == 200
    assert up_m.json()["status"] == "INACTIVE"

    # Remove Rohan from Web Dev
    rm_team = e2e_client.delete(f"/api/members/{mem2['id']}/teams/{team1['id']}", headers=admin_headers)
    assert rm_team.status_code == 200

    # Delete Rohan
    del_mem = e2e_client.delete(f"/api/members/{mem2['id']}", headers=admin_headers)
    assert del_mem.status_code == 200

    # Verify count decremented
    dash_after = e2e_client.get("/api/dashboard/stats", headers=member_headers).json()
    assert dash_after["total_members"] == 2
