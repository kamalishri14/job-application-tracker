"""
Seed the database with sample job applications — useful for screenshots,
demos, or just trying the app out before you start logging real applications.

Run with: python seed.py
"""
from datetime import date, timedelta
import random

from app import create_app
from models import db, Application

SAMPLE_DATA = [
    ("TCS", "Data Analyst", "Chennai", "Applied", 30),
    ("Infosys", "ETL Developer", "Pune", "Interview", 25),
    ("Wipro", "Python Developer", "Bengaluru", "Applied", 22),
    ("Accenture", "Data Engineer", "Hyderabad", "Rejected", 20),
    ("Cognizant", "SQL Developer", "Chennai", "Applied", 18),
    ("HCLTech", "Business Analyst", "Remote", "Interview", 15),
    ("Capgemini", "Software Developer", "Bengaluru", "Applied", 12),
    ("Tech Mahindra", "Data Analyst", "Pune", "Offer", 10),
    ("IBM", "Python Full Stack Developer", "Bengaluru", "Applied", 8),
    ("Deloitte", "Data Analyst", "Remote", "Applied", 5),
    ("Mu Sigma", "Junior Data Analyst", "Bengaluru", "Rejected", 28),
    ("Zoho", "Software Engineer", "Chennai", "Applied", 3),
]

NOTES = [
    "Applied via referral.",
    "Recruiter screen scheduled.",
    "Waiting on HR response.",
    "Submitted through company careers page.",
    "Found via LinkedIn.",
    "",
]


def seed():
    app = create_app()
    with app.app_context():
        if Application.query.count() > 0:
            confirm = input("Database already has data. Add sample rows anyway? (y/n): ")
            if confirm.lower() != "y":
                print("Skipped seeding.")
                return

        for company, role, location, status, days_ago in SAMPLE_DATA:
            entry = Application(
                company=company,
                role=role,
                location=location,
                status=status,
                applied_date=date.today() - timedelta(days=days_ago),
                notes=random.choice(NOTES),
            )
            db.session.add(entry)

        db.session.commit()
        print(f"Seeded {len(SAMPLE_DATA)} sample applications.")


if __name__ == "__main__":
    seed()
