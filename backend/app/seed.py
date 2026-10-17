import sys
import os
from datetime import date

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal, Base, engine
from app.models import User, Member, Team, Membership
from app.auth import hash_password


def seed_database():
    print("🌱 Resetting and seeding ACM NITK database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Create Users
        admin_user = User(
            email="admin@nitk.edu.in",
            password_hash=hash_password("admin123"),
            role="ADMIN",
        )
        regular_user = User(
            email="member@nitk.edu.in",
            password_hash=hash_password("member123"),
            role="MEMBER",
        )
        db.add_all([admin_user, regular_user])
        db.commit()
        db.refresh(admin_user)
        db.refresh(regular_user)

        # 2. Create Members
        members_data = [
            {
                "full_name": "Aditya Rao",
                "email": "aditya.rao@nitk.edu.in",
                "phone": "+91 98765 43210",
                "department": "Computer Science & Engineering",
                "year": 4,
                "status": "ACTIVE",
                "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Aditya",
                "bio": "ACM NITK Chair & Full-Stack developer passionate about distributed systems.",
                "date_joined": date(2023, 8, 15),
                "user_id": admin_user.id,
            },
            {
                "full_name": "Pooja Hegde",
                "email": "pooja.hegde@nitk.edu.in",
                "phone": "+91 98765 43211",
                "department": "Information Technology",
                "year": 3,
                "status": "ACTIVE",
                "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Pooja",
                "bio": "Web Team Lead. Frontend specialist with React, Next.js and UI/UX design.",
                "date_joined": date(2024, 1, 10),
                "user_id": regular_user.id,
            },
            {
                "full_name": "Rahul Verma",
                "email": "rahul.verma@nitk.edu.in",
                "phone": "+91 98765 43212",
                "department": "Computer Science & Engineering",
                "year": 3,
                "status": "ACTIVE",
                "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Rahul",
                "bio": "Systems enthusiast, Linux kernel hacker, and cloud infrastructure lover.",
                "date_joined": date(2024, 2, 5),
            },
            {
                "full_name": "Sneha Nair",
                "email": "sneha.nair@nitk.edu.in",
                "phone": "+91 98765 43213",
                "department": "Electronics & Communication",
                "year": 3,
                "status": "ACTIVE",
                "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Sneha",
                "bio": "AI/ML Lead focusing on Computer Vision and NLP model fine-tuning.",
                "date_joined": date(2024, 1, 20),
            },
            {
                "full_name": "Karthik Bhat",
                "email": "karthik.bhat@nitk.edu.in",
                "phone": "+91 98765 43214",
                "department": "Computer Science & Engineering",
                "year": 4,
                "status": "ACTIVE",
                "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Karthik",
                "bio": "Competitive Programming Lead. Candidate Master on Codeforces, ICPC regionalist.",
                "date_joined": date(2023, 9, 1),
            },
            {
                "full_name": "Ananya Sharma",
                "email": "ananya.sharma@nitk.edu.in",
                "phone": "+91 98765 43215",
                "department": "Information Technology",
                "year": 2,
                "status": "ACTIVE",
                "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Ananya",
                "bio": "Junior web developer working with TypeScript, Tailwind, and Node.js.",
                "date_joined": date(2025, 8, 20),
            },
            {
                "full_name": "Vikram Shenoy",
                "email": "vikram.shenoy@nitk.edu.in",
                "phone": "+91 98765 43216",
                "department": "Electrical & Electronics",
                "year": 2,
                "status": "ACTIVE",
                "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Vikram",
                "bio": "Machine learning researcher and embedded systems explorer.",
                "date_joined": date(2025, 9, 15),
            },
            {
                "full_name": "Meera Joshi",
                "email": "meera.joshi@nitk.edu.in",
                "phone": "+91 98765 43217",
                "department": "Mechanical Engineering",
                "year": 2,
                "status": "ACTIVE",
                "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Meera",
                "bio": "Cross-disciplinary dev interested in algorithmic design and simulation.",
                "date_joined": date(2025, 10, 1),
            },
            {
                "full_name": "Rohan Deshmukh",
                "email": "rohan.deshmukh@nitk.edu.in",
                "phone": "+91 98765 43218",
                "department": "Computer Science & Engineering",
                "year": 1,
                "status": "ACTIVE",
                "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Rohan",
                "bio": "Freshman enthusiastic about open-source and web development.",
                "date_joined": date(2026, 9, 10),
            },
            {
                "full_name": "Tanvi Kulkarni",
                "email": "tanvi.kulkarni@nitk.edu.in",
                "phone": "+91 98765 43219",
                "department": "Information Technology",
                "year": 1,
                "status": "INACTIVE",
                "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Tanvi",
                "bio": "Currently on academic leave for exchange semester.",
                "date_joined": date(2026, 8, 12),
            },
            {
                "full_name": "Varun Kamath",
                "email": "varun.kamath@nitk.edu.in",
                "phone": "+91 98765 43220",
                "department": "Computer Science & Engineering",
                "year": 4,
                "status": "ALUMNI",
                "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Varun",
                "bio": "Former Web Team Head (2024-2025). Now SDE at Microsoft.",
                "date_joined": date(2022, 8, 10),
            },
            {
                "full_name": "Divya Pai",
                "email": "divya.pai@nitk.edu.in",
                "phone": "+91 98765 43221",
                "department": "Electronics & Communication",
                "year": 4,
                "status": "ALUMNI",
                "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=Divya",
                "bio": "Former AI/ML lead. Graduate researcher at CMU.",
                "date_joined": date(2022, 9, 1),
            },
        ]

        created_members = []
        for m_data in members_data:
            mem = Member(**m_data)
            db.add(mem)
            created_members.append(mem)
        db.commit()

        # Refresh member IDs
        for m in created_members:
            db.refresh(m)

        # Mapping names to member objects
        mem_map = {m.full_name: m for m in created_members}

        # 3. Create Teams
        teams_data = [
            {
                "name": "Web Development",
                "description": "Designs, develops, and maintains all official ACM NITK web portals and student tools.",
                "team_lead_id": mem_map["Pooja Hegde"].id,
            },
            {
                "name": "Systems & Security",
                "description": "Explores Linux systems, cloud infrastructure, network protocols, and cybersecurity challenges.",
                "team_lead_id": mem_map["Rahul Verma"].id,
            },
            {
                "name": "AI/ML SIG",
                "description": "Special Interest Group dedicated to machine learning, computer vision, deep neural networks, and NLP research.",
                "team_lead_id": mem_map["Sneha Nair"].id,
            },
            {
                "name": "Competitive Programming",
                "description": "Trains members in advanced algorithms and data structures for ICPC, HashCode, and competitive coding contests.",
                "team_lead_id": mem_map["Karthik Bhat"].id,
            },
        ]

        created_teams = []
        for t_data in teams_data:
            t = Team(**t_data)
            db.add(t)
            created_teams.append(t)
        db.commit()

        for t in created_teams:
            db.refresh(t)

        team_map = {t.name: t for t in created_teams}

        # 4. Create Memberships (Many-to-Many with different designations!)
        memberships_data = [
            # Pooja: Lead in Web Dev, Core in AI/ML
            (mem_map["Pooja Hegde"].id, team_map["Web Development"].id, "Team Lead"),
            (mem_map["Pooja Hegde"].id, team_map["AI/ML SIG"].id, "Core Member"),

            # Aditya: Senior Member in Web Dev, Senior Member in Systems
            (mem_map["Aditya Rao"].id, team_map["Web Development"].id, "Senior Advisor"),
            (mem_map["Aditya Rao"].id, team_map["Systems & Security"].id, "Executive Member"),

            # Rahul: Lead in Systems, Executive in CP
            (mem_map["Rahul Verma"].id, team_map["Systems & Security"].id, "Team Lead"),
            (mem_map["Rahul Verma"].id, team_map["Competitive Programming"].id, "Executive"),

            # Sneha: Lead in AI/ML
            (mem_map["Sneha Nair"].id, team_map["AI/ML SIG"].id, "Team Lead"),

            # Karthik: Lead in CP, Core in Systems
            (mem_map["Karthik Bhat"].id, team_map["Competitive Programming"].id, "Team Lead"),
            (mem_map["Karthik Bhat"].id, team_map["Systems & Security"].id, "Senior Core"),

            # Ananya: Junior Dev in Web Dev
            (mem_map["Ananya Sharma"].id, team_map["Web Development"].id, "Junior Developer"),

            # Vikram: Core in AI/ML
            (mem_map["Vikram Shenoy"].id, team_map["AI/ML SIG"].id, "Core Member"),

            # Meera: Junior Dev in CP
            (mem_map["Meera Joshi"].id, team_map["Competitive Programming"].id, "Junior Member"),

            # Rohan: Mentee in Web Dev
            (mem_map["Rohan Deshmukh"].id, team_map["Web Development"].id, "Mentee"),

            # Tanvi: Member in Web Dev
            (mem_map["Tanvi Kulkarni"].id, team_map["Web Development"].id, "Member"),

            # Alumni Varun: Former Lead in Web Dev
            (mem_map["Varun Kamath"].id, team_map["Web Development"].id, "Former Lead"),

            # Alumni Divya: Former Lead in AI/ML
            (mem_map["Divya Pai"].id, team_map["AI/ML SIG"].id, "Former Lead"),
        ]

        for m_id, t_id, desig in memberships_data:
            ms = Membership(member_id=m_id, team_id=t_id, designation=desig)
            db.add(ms)
        db.commit()

        print(f"✅ Successfully seeded:")
        print(f"   - {len(members_data)} members")
        print(f"   - {len(teams_data)} teams")
        print(f"   - {len(memberships_data)} memberships")
        print(f"   - 2 users: admin@nitk.edu.in (ADMIN), member@nitk.edu.in (MEMBER)")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
