# Membership Management System — Simplified Architecture & Execution Plan

## 1. Specification Comparison & Requirements Checklist

Every mandatory requirement from `ACM NITK Web Team Recruitment.docx` is preserved and mapped below without optional bloat.

| # | Mandatory Requirement | Implementation Strategy | Verification Method |
|---|----------------------|-------------------------|---------------------|
| 1 | Registration, login, logout | FastAPI auth endpoints, JWT in `localStorage`, logout clears token | API test + manual UI flow |
| 2 | Password hashing & protected routes | `passlib[bcrypt]`, client route guard `<ProtectedRoute>` | Unit test for hash + unauth redirect |
| 3 | Backend RBAC | FastAPI dependency `require_admin` checking `user.role == 'ADMIN'` | Non-admin gets `403 Forbidden` on admin APIs |
| 4 | Complete Member CRUD | `POST/GET/PUT/DELETE` on `/api/members` | Pytest CRUD suite + UI action verification |
| 5 | Complete Team CRUD | `POST/GET/PUT/DELETE` on `/api/teams` | Pytest CRUD suite + UI action verification |
| 6 | Member Profile Information | Name, email, phone, department, year, status, avatar URL, bio | Schema validation + Detail page render |
| 7 | Multi-team assignment with designation | Association table `memberships` with `member_id`, `team_id`, `designation` | Unit test for M:N assignments & unique pair check |
| 8 | Member search by name | Case-insensitive SQL `ILIKE` on `full_name` | Query verification with partial strings |
| 9 | Filters: team, designation, dept, year, status | Dynamic SQL `WHERE` clauses on query parameters | Test individual filter queries |
| 10 | Multiple filters simultaneously | Combined `AND` clauses in SQLAlchemy query | Test multi-param combinations |
| 11 | Sorting by name, year, date joined | SQL `ORDER BY` with `asc`/`desc` | Query verification for each sort key |
| 12 | Pagination & clear-all-filters | SQL `LIMIT` & `OFFSET`, UI reset button | Test page transitions & reset state |
| 13 | Empty, loading, error states | React conditional state banners/alerts | Inspect network delays & zero-result queries |
| 14 | Team descriptions, leads, rosters, counts | `teams` joined with `members` & `memberships`, count aggregation | Verify team page shows lead & member roster |
| 15 | Live Dashboard Statistics | DB aggregations (`COUNT`, `GROUP BY`) for totals, active/inactive, dept, year, teams, recent | Compare dashboard numbers with direct SQL counts |
| 16 | Relational DB, FKs, validation, HTTP codes | PostgreSQL, foreign keys, Pydantic v2 schemas, standard HTTP codes | Schema inspection & Pydantic validation tests |
| 17 | Responsive layouts (Desktop, Tablet, Mobile) | Clean plain CSS with media queries (`@media (max-width: 768px)`) | Viewport resizing checks (375px, 768px, 1200px) |
| 18 | Understandable code & Git history | Layered MVC structure, conventional Git commits | Git log review |
| 19 | Complete README | Setup steps, schema/ER diagram, endpoints, known limits | Fresh clone verification against README |
| 20 | Demo video guide | Documented walkthrough script covering all 5 pages | Self-review against grading rubric |

---

## 2. Simplified Stack & Architecture

- **Frontend:** React (Vite) + JavaScript (plain JSX, no TypeScript overhead).
- **Styling:** Plain CSS (`index.css` with clean layout, table, card, and form styles; no Tailwind/Radix dependencies).
- **Backend:** Python 3.12 + FastAPI + Pydantic v2.
- **Database:** PostgreSQL (with automatic SQLite fallback only if local PostgreSQL environment blocks execution).
- **ORM:** SQLAlchemy 2.0 with clean session dependency.
- **Auth:** Passlib (`bcrypt`) for password hashing, PyJWT for bearer tokens.

### Simplified Folder Structure:
```
acm_web/
├── backend/
│   ├── app/
│   │   ├── database.py       # Engine, session, declarative base
│   │   ├── models.py         # User, Member, Team, Membership
│   │   ├── schemas.py        # Pydantic request/response schemas
│   │   ├── auth.py           # Password hashing, JWT, require_admin dependency
│   │   ├── routes_auth.py    # /api/auth (register, login, me)
│   │   ├── routes_members.py # /api/members (CRUD, search, filter, sort, paginate)
│   │   ├── routes_teams.py   # /api/teams (CRUD, rosters, lead assignment)
│   │   ├── routes_stats.py   # /api/dashboard (dynamic aggregations)
│   │   ├── seed.py           # Realistic ACM NITK seed script
│   │   └── main.py           # FastAPI entrypoint, CORS, router mounts
│   ├── requirements.txt
│   └── test_backend.py       # Direct pytest suite for auth, RBAC, CRUD
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── AuthPage.jsx          # Page 1: Login / Register toggle
│   │   │   ├── DashboardPage.jsx     # Page 2: Statistic cards & distribution tables/bars
│   │   │   ├── MembersPage.jsx       # Page 3: Member list, search, multi-filters, pagination
│   │   │   ├── MemberDetailPage.jsx   # Page 4: Full profile & team assignment management
│   │   │   └── TeamsPage.jsx         # Page 5: Team cards, member rosters, team CRUD
│   │   ├── components/
│   │   │   ├── Navbar.jsx            # Simple top navigation with user role & logout
│   │   │   └── ProtectedRoute.jsx    # Client auth redirect guard
│   │   ├── api.js                    # Fetch wrapper attaching JWT bearer token
│   │   ├── App.jsx                   # Routes definition
│   │   ├── index.css                 # Plain, responsive CSS
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── README.md
└── PLAN.md
```

---

## 3. Database Schema (No Bloat)

1. **`users`**: `id` (int/uuid PK), `email` (unique), `password_hash`, `role` (`ADMIN` or `MEMBER`), `created_at`.
2. **`members`**: `id` (PK), `user_id` (FK to `users.id`, nullable), `full_name`, `email` (unique), `phone`, `department`, `year`, `status` (`ACTIVE`/`INACTIVE`), `avatar_url`, `bio`, `date_joined`.
3. **`teams`**: `id` (PK), `name` (unique), `description`, `team_lead_id` (FK to `members.id`, nullable on delete set null).
4. **`memberships`**: `id` (PK), `member_id` (FK to `members.id`, cascade delete), `team_id` (FK to `teams.id`, cascade delete), `designation`, `joined_at`.
   * **Constraint:** `UNIQUE(member_id, team_id)`.

---

## 4. Simplified Phased Implementation Plan

- **Phase 1: Backend Foundation & DB Models**
  - Setup virtualenv, install FastAPI, SQLAlchemy, Pydantic, Passlib, PyJWT.
  - Create `database.py`, `models.py`, `schemas.py`.
  - Connect to DB (PostgreSQL target, fallback SQLite if blocked).
  - Verify tables create cleanly.

- **Phase 2: Auth & Role-Based Authorization**
  - Implement password hashing, JWT issue/verify.
  - Implement `routes_auth.py` (`register`, `login`, `me`).
  - Implement `require_admin` dependency for protected mutations.
  - Run auth & RBAC tests.

- **Phase 3: Core CRUD & Business Logic**
  - Implement `routes_teams.py` (CRUD, team lead, member roster).
  - Implement `routes_members.py` (CRUD, multi-team assignments, compound filters, search, sort, pagination).
  - Implement `routes_stats.py` (live counts, department/year/team breakdowns, recent members).
  - Create `seed.py` with realistic ACM NITK data.
  - Run focused backend tests on all endpoints.

- **Phase 4: Frontend Scaffolding & Plain CSS**
  - Initialize Vite React project (JS, plain CSS).
  - Setup `index.css` with responsive grid, card, table, badge, and form styles.
  - Setup `api.js` for authenticated API calls.
  - Implement `Navbar.jsx` and `ProtectedRoute.jsx`.

- **Phase 5: The 5 Required Frontend Pages**
  - **Page 1: AuthPage (Login/Register)** with error states and immediate token storage.
  - **Page 2: DashboardPage** with live stat cards, simple CSS bar/distribution tables, and recent members.
  - **Page 3: MembersPage** with search input, multi-filter dropdowns, sorting, pagination, and admin Create Member form.
  - **Page 4: MemberDetailPage** showing complete profile, status, bio, and multi-team assignments with designation editor.
  - **Page 5: TeamsPage** showing team cards, team leads, rosters, member counts, and admin Create Team form.

- **Phase 6: Verification, README & Review**
  - Execute full backend test suite (`pytest test_backend.py`).
  - Verify all 20 mandatory requirements in browser across desktop and mobile widths.
  - Write complete `README.md` with setup steps, schema diagram, endpoints table, and demo video script.
