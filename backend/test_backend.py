import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import User, Member, Team, Membership
from app.auth import hash_password

# Test SQLite in-memory database using StaticPool
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_tokens(client, db):
    # Create admin
    admin = User(email="admin@test.com", password_hash=hash_password("adminpass"), role="ADMIN")
    # Create regular member
    reg = User(email="member@test.com", password_hash=hash_password("memberpass"), role="MEMBER")
    db.add_all([admin, reg])
    db.commit()

    admin_login = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "adminpass"})
    admin_token = admin_login.json()["access_token"]

    reg_login = client.post("/api/auth/login", json={"email": "member@test.com", "password": "memberpass"})
    reg_token = reg_login.json()["access_token"]

    return {
        "admin": {"Authorization": f"Bearer {admin_token}"},
        "member": {"Authorization": f"Bearer {reg_token}"},
    }


# ==========================================
# 1. TEAM MANAGEMENT TESTS
# ==========================================

def test_team_crud_and_rbac(client, auth_tokens):
    admin_headers = auth_tokens["admin"]
    member_headers = auth_tokens["member"]

    # Regular member cannot create a team -> 403 Forbidden
    res = client.post("/api/teams", json={"name": "Web Team", "description": "Web dev"}, headers=member_headers)
    assert res.status_code == 403

    # Admin can create a team -> 201 Created
    res = client.post("/api/teams", json={"name": "Web Team", "description": "Web dev"}, headers=admin_headers)
    assert res.status_code == 201
    team_data = res.json()
    team_id = team_data["id"]
    assert team_data["name"] == "Web Team"
    assert team_data["member_count"] == 0

    # Duplicate team name -> 400 Bad Request
    res_dup = client.post("/api/teams", json={"name": "Web Team"}, headers=admin_headers)
    assert res_dup.status_code == 400

    # Authenticated member can list teams -> 200 OK
    res_list = client.get("/api/teams", headers=member_headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1

    # Admin updates team
    res_up = client.put(f"/api/teams/{team_id}", json={"description": "Updated Web description"}, headers=admin_headers)
    assert res_up.status_code == 200
    assert res_up.json()["description"] == "Updated Web description"

    # Admin deletes team -> 200 OK
    res_del = client.delete(f"/api/teams/{team_id}", headers=admin_headers)
    assert res_del.status_code == 200

    # Getting deleted team -> 404
    res_get = client.get(f"/api/teams/{team_id}", headers=member_headers)
    assert res_get.status_code == 404


# ==========================================
# 2. MEMBER CRUD & MEMBERSHIP TESTS
# ==========================================

def test_member_crud_and_multi_team_assignments(client, auth_tokens):
    admin_headers = auth_tokens["admin"]
    member_headers = auth_tokens["member"]

    # Create two teams
    t1 = client.post("/api/teams", json={"name": "Web Dev"}, headers=admin_headers).json()
    t2 = client.post("/api/teams", json={"name": "AI/ML"}, headers=admin_headers).json()

    # Regular member cannot create a member -> 403
    create_payload = {
        "full_name": "Aditya Rao",
        "email": "aditya@nitk.edu.in",
        "phone": "9876543210",
        "department": "CSE",
        "year": 3,
        "status": "ACTIVE",
        "teams": [
            {"team_id": t1["id"], "designation": "Lead"},
            {"team_id": t2["id"], "designation": "Core Member"},
        ],
    }
    res = client.post("/api/members", json=create_payload, headers=member_headers)
    assert res.status_code == 403

    # Admin creates member with 2 team assignments -> 201 Created
    res = client.post("/api/members", json=create_payload, headers=admin_headers)
    assert res.status_code == 201
    member = res.json()
    m_id = member["id"]
    assert member["full_name"] == "Aditya Rao"
    assert len(member["memberships"]) == 2
    # Check that each team assignment has its distinct designation
    desigs = {m["team_name"]: m["designation"] for m in member["memberships"]}
    assert desigs["Web Dev"] == "Lead"
    assert desigs["AI/ML"] == "Core Member"

    # Team detail now shows member in roster
    team_detail = client.get(f"/api/teams/{t1['id']}", headers=member_headers).json()
    assert team_detail["member_count"] == 1
    assert team_detail["roster"][0]["full_name"] == "Aditya Rao"
    assert team_detail["roster"][0]["designation"] == "Lead"

    # Duplicate team assignment fails -> 400 Bad Request
    res_dupe_assign = client.post(
        f"/api/members/{m_id}/teams",
        json={"team_id": t1["id"], "designation": "Another Role"},
        headers=admin_headers,
    )
    assert res_dupe_assign.status_code == 400

    # Update designation in team -> 200 OK
    res_up_desig = client.put(
        f"/api/members/{m_id}/teams/{t1['id']}",
        json={"designation": "Senior Lead"},
        headers=admin_headers,
    )
    assert res_up_desig.status_code == 200
    assert res_up_desig.json()["designation"] == "Senior Lead"

    # Remove member from AI/ML team -> 200 OK
    res_rm = client.delete(f"/api/members/{m_id}/teams/{t2['id']}", headers=admin_headers)
    assert res_rm.status_code == 200

    # Member detail now has only 1 membership
    m_detail = client.get(f"/api/members/{m_id}", headers=member_headers).json()
    assert len(m_detail["memberships"]) == 1
    assert m_detail["memberships"][0]["team_name"] == "Web Dev"

    # Delete member -> 200 OK
    res_del_mem = client.delete(f"/api/members/{m_id}", headers=admin_headers)
    assert res_del_mem.status_code == 200

    # Team roster is now 0
    t1_after = client.get(f"/api/teams/{t1['id']}", headers=member_headers).json()
    assert t1_after["member_count"] == 0


# ==========================================
# 3. SEARCH, SIMULTANEOUS FILTERS, SORT, PAGINATION
# ==========================================

def test_directory_search_filter_sort_pagination(client, auth_tokens):
    admin_headers = auth_tokens["admin"]
    member_headers = auth_tokens["member"]

    # Setup Team
    team = client.post("/api/teams", json={"name": "Competitive Programming"}, headers=admin_headers).json()
    tid = team["id"]

    # Create test members
    members_to_create = [
        {"full_name": "Alice Johnson", "email": "alice@nitk.edu.in", "department": "CSE", "year": 1, "status": "ACTIVE"},
        {"full_name": "Bob Smith", "email": "bob@nitk.edu.in", "department": "IT", "year": 2, "status": "ACTIVE"},
        {"full_name": "Charlie Brown", "email": "charlie@nitk.edu.in", "department": "ECE", "year": 3, "status": "INACTIVE"},
        {"full_name": "David Miller", "email": "david@nitk.edu.in", "department": "CSE", "year": 4, "status": "ALUMNI"},
        {"full_name": "Eve Davis", "email": "eve@nitk.edu.in", "department": "CSE", "year": 2, "status": "ACTIVE"},
    ]
    created = []
    for m in members_to_create:
        res = client.post("/api/members", json=m, headers=admin_headers)
        created.append(res.json())

    # Assign Alice and Eve to team
    client.post(f"/api/members/{created[0]['id']}/teams", json={"team_id": tid, "designation": "Executive"}, headers=admin_headers)
    client.post(f"/api/members/{created[4]['id']}/teams", json={"team_id": tid, "designation": "Mentee"}, headers=admin_headers)

    # 1. Search by name (case-insensitive)
    res_search = client.get("/api/members?search=alice", headers=member_headers).json()
    assert res_search["total"] == 1
    assert res_search["members"][0]["full_name"] == "Alice Johnson"

    # 2. Search by email
    res_email = client.get("/api/members?search=bob@nitk", headers=member_headers).json()
    assert res_email["total"] == 1
    assert res_email["members"][0]["full_name"] == "Bob Smith"

    # 3. Filter by department
    res_dept = client.get("/api/members?department=CSE", headers=member_headers).json()
    assert res_dept["total"] == 3

    # 4. Filter by year
    res_yr = client.get("/api/members?year=2", headers=member_headers).json()
    assert res_yr["total"] == 2

    # 5. Filter by status (ALUMNI)
    res_alumni = client.get("/api/members?status=ALUMNI", headers=member_headers).json()
    assert res_alumni["total"] == 1
    assert res_alumni["members"][0]["full_name"] == "David Miller"

    # 6. Filter by team
    res_team = client.get(f"/api/members?team_id={tid}", headers=member_headers).json()
    assert res_team["total"] == 2

    # 7. Filter by designation
    res_desig = client.get("/api/members?designation=Executive", headers=member_headers).json()
    assert res_desig["total"] == 1
    assert res_desig["members"][0]["full_name"] == "Alice Johnson"

    # 8. SIMULTANEOUS COMPOUND FILTER: CSE + Year 2 + ACTIVE + in CP team
    res_compound = client.get(
        f"/api/members?department=CSE&year=2&status=ACTIVE&team_id={tid}",
        headers=member_headers,
    ).json()
    assert res_compound["total"] == 1
    assert res_compound["members"][0]["full_name"] == "Eve Davis"

    # 9. Sorting by name desc
    res_sort_desc = client.get("/api/members?sort_by=name&order=desc", headers=member_headers).json()
    names = [m["full_name"] for m in res_sort_desc["members"]]
    assert names[0] == "Eve Davis"
    assert names[-1] == "Alice Johnson"

    # 10. Sorting by year asc
    res_sort_yr = client.get("/api/members?sort_by=year&order=asc", headers=member_headers).json()
    years = [m["year"] for m in res_sort_yr["members"]]
    assert years == sorted(years)

    # 11. Pagination: limit=2, page=1 and page=2
    res_p1 = client.get("/api/members?limit=2&page=1&sort_by=name&order=asc", headers=member_headers).json()
    assert res_p1["total"] == 5
    assert len(res_p1["members"]) == 2
    assert res_p1["page"] == 1

    res_p2 = client.get("/api/members?limit=2&page=2&sort_by=name&order=asc", headers=member_headers).json()
    assert len(res_p2["members"]) == 2
    assert res_p2["page"] == 2
    # Ensure distinct pages
    p1_names = {m["full_name"] for m in res_p1["members"]}
    p2_names = {m["full_name"] for m in res_p2["members"]}
    assert len(p1_names.intersection(p2_names)) == 0


# ==========================================
# 4. DASHBOARD STATISTICS TESTS
# ==========================================

def test_dashboard_statistics(client, auth_tokens):
    admin_headers = auth_tokens["admin"]
    member_headers = auth_tokens["member"]

    # Create team
    t = client.post("/api/teams", json={"name": "DevOps"}, headers=admin_headers).json()

    # Create members with different statuses & departments
    client.post("/api/members", json={"full_name": "M1", "email": "m1@nitk.edu.in", "department": "CSE", "year": 1, "status": "ACTIVE"}, headers=admin_headers)
    client.post("/api/members", json={"full_name": "M2", "email": "m2@nitk.edu.in", "department": "CSE", "year": 2, "status": "ACTIVE"}, headers=admin_headers)
    client.post("/api/members", json={"full_name": "M3", "email": "m3@nitk.edu.in", "department": "ECE", "year": 3, "status": "INACTIVE"}, headers=admin_headers)
    client.post("/api/members", json={"full_name": "M4", "email": "m4@nitk.edu.in", "department": "IT", "year": 4, "status": "ALUMNI"}, headers=admin_headers)

    # Unauthenticated access -> 401
    assert client.get("/api/dashboard/stats").status_code == 401

    # Authenticated access
    res = client.get("/api/dashboard/stats", headers=member_headers)
    assert res.status_code == 200
    stats = res.json()

    assert stats["total_members"] == 4
    assert stats["active_count"] == 2
    assert stats["inactive_count"] == 1
    assert stats["alumni_count"] == 1
    assert stats["total_teams"] == 1

    # Department distribution check
    dept_map = {d["name"]: d["count"] for d in stats["department_distribution"]}
    assert dept_map["CSE"] == 2
    assert dept_map["ECE"] == 1
    assert dept_map["IT"] == 1

    # Year distribution check
    year_map = {y["name"]: y["count"] for y in stats["year_distribution"]}
    assert year_map["Year 1"] == 1
    assert year_map["Year 2"] == 1
    assert year_map["Year 3"] == 1
    assert year_map["Year 4"] == 1

    # Recent members check
    assert len(stats["recent_members"]) == 4
