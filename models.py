from datetime import date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

STATUS_CHOICES = ["Applied", "Interview", "Offer", "Rejected"]


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    job_link = db.Column(db.String(300), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="Applied")
    applied_date = db.Column(db.Date, nullable=False, default=date.today)
    notes = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    def to_dict(self):
        return {
            "id": self.id,
            "company": self.company,
            "role": self.role,
            "job_link": self.job_link,
            "status": self.status,
            "applied_date": self.applied_date.isoformat() if self.applied_date else None,
            "notes": self.notes,
            "location": self.location,
        }
