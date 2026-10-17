# ACM NITK Membership Management System — Video Walkthrough Script
**Target Duration:** ~3 to 5 minutes  
**Format:** Screen recording with voiceover (QuickTime / OBS / Loom)

---

### Pre-Recording Setup Checklist
1. Ensure the backend server is running (`uvicorn app.main:app --reload` on port 8000).
2. Ensure the frontend dev server is running (`npm run dev` on port 5173).
3. Ensure the database has been seeded with demo data (`python app/seed.py`).
4. Have your browser open at `http://localhost:5173` in an incognito window so you start at the login screen.
5. Local Demo Credentials:
   * **Admin Account:** `admin@nitk.edu.in` | Password: `admin123`
   * **Member Account:** `member@nitk.edu.in` | Password: `member123`

---

### Step-by-Step Walkthrough (Scene-by-Scene)

#### **Scene 1: Introduction & Technology Stack (~30 seconds)**
* **On Screen:** Browser showing the Login / Registration screen (`http://localhost:5173/login`).
* **Voiceover:**
  > *"Hello! This is my submission for the ACM NITK Web Team Recruitment task: the Membership Management System. The application is built using a decoupled architecture with a Python and FastAPI backend, SQLAlchemy ORM, and SQLite database with foreign-key constraints, paired with a React and Vite frontend styled with responsive plain CSS without external UI bloat."*

#### **Scene 2: Registration & Public Security (~30 seconds)**
* **On Screen:**
  1. Click the "Register" tab on the auth card.
  2. Highlight that there is no role selector—users cannot escalate themselves to administrators.
  3. Enter `newstudent@nitk.edu.in`, password `password123`, and click "Create Account".
  4. Show successful login redirection to the Dashboard.
* **Voiceover:**
  > *"First, let's test user registration. Notice that the registration form only accepts an email and password; by design, public registration strictly assigns the regular MEMBER role to prevent unauthorized privilege escalation. Once submitted, passwords are securely hashed using bcrypt on the server, and a JWT token is stored securely for authenticated sessions."*

#### **Scene 3: Regular Member Read-Only Experience (~45 seconds)**
* **On Screen:**
  1. Show the navbar badge displaying `MEMBER`.
  2. Navigate to **Members Directory** (`/members`).
  3. Point out that the "+ Add New Member", "Edit", and "Delete" buttons are hidden for regular members.
  4. Navigate to **Teams** (`/teams`).
  5. Show that "+ Create Team", "Edit", and "Delete Team" are also absent, but "View Roster" works cleanly.
* **Voiceover:**
  > *"As a regular member, the interface is read-only. Members cannot see administrative controls, and if a regular member attempts to send create, update, or delete requests directly to the API, the backend enforces Role-Based Access Control and returns an immediate 403 Forbidden."*

#### **Scene 4: Admin Authentication & Live Dashboard Analytics (~45 seconds)**
* **On Screen:**
  1. Click "Logout" in the navbar.
  2. Log in using `admin@nitk.edu.in` / `admin123`.
  3. Show the navbar badge now displaying `ADMIN`.
  4. On the **Dashboard**, highlight:
     * Total Members, Active, Inactive, Alumni, and Total Teams cards.
     * The dynamic department-wise, year-wise, and team-wise distribution bars.
     * The recently added members list.
* **Voiceover:**
  > *"Now let's log in as an administrator. The navbar updates with the purple ADMIN badge. On the Dashboard, all summary cards, distribution bars, and recent member records are derived in real-time from database aggregations—none of this data is hardcoded."*

#### **Scene 5: Members Directory — Search, Multi-Filter, Sort & Pagination (~60 seconds)**
* **On Screen:**
  1. Go to `/members`.
  2. Type `Pooja` into the search box and press Enter (shows Pooja Hegde).
  3. Click "Clear Filters".
  4. Apply compound filters simultaneously:
     * Select Department: `Computer Science & Engineering`
     * Select Year: `Year 1`
     * Select Status: `INACTIVE`
     * Click Search (shows Rohan Deshmukh).
  5. Click "Clear Filters".
  6. Test sorting by "Year" and "Date Joined".
  7. Test pagination by clicking "Next" and "Previous".
* **Voiceover:**
  > *"In the Members Directory, we have real-time search across names and emails, alongside compound filtering. We can filter by department, year of study, team, designation, and status simultaneously. Sorting works on name, year, and date joined, and pagination efficiently limits database queries using SQL limit and offset."*

#### **Scene 6: Multi-Team Assignment with Distinct Designations (~60 seconds)**
* **On Screen:**
  1. Click on `Pooja Hegde` to open `/members/:id`.
  2. Point out that Pooja is already assigned to two teams:
     * *Web Development* with designation **Team Lead**
     * *AI/ML SIG* with designation **Core Member**
  3. Click "+ Assign Team" and assign her to a third team: *Competitive Programming* with designation **Algorithm Specialist**.
  4. Show the new row appear immediately.
  5. Click "Edit Role" on one of the teams and change it inline.
  6. Show "Remove" removes that specific team assignment without affecting her other memberships or profile.
* **Voiceover:**
  > *"A key requirement of the specification is that members can belong to multiple teams, with a distinct designation in each team. In Pooja's profile, we see she is the Team Lead in Web Development and a Core Member in AI/ML. As an admin, I can assign her to additional teams with custom roles, edit designations inline, or remove memberships safely."*

#### **Scene 7: Teams Management & Rosters (~40 seconds)**
* **On Screen:**
  1. Go to `/teams`.
  2. Click "+ Create New Team", enter name `DevOps & Cloud`, description `Cloud infrastructure & Kubernetes`, assign a team lead, and submit.
  3. Show the new team card created.
  4. Click "View Roster" on *Web Development* to view the modal with all assigned members and their roles.
* **Voiceover:**
  > *"On the Teams page, admins can create new teams and assign team leads. Clicking 'View Roster' opens a clean modal listing every student belonging to that team and their role."*

#### **Scene 8: Conclusion & Testing Summary (~20 seconds)**
* **On Screen:**
  1. Switch to terminal showing `pytest` running and passing 16/16 tests.
  2. Conclude the video.
* **Voiceover:**
  > *"All 20 mandatory requirements from the specification—including full CRUD, multi-team assignments, compound filters, live dashboard metrics, role-based authorization, and plain responsive CSS—are fully implemented, tested, and passing all automated test suites. Thank you!"*
