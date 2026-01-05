# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


def generate_id(prefix: str, model) -> str:
    """
    Generate IDs like STU-2025-0001 based on current year and count.
    """
    year = datetime.now().year
    count = model.query.count() + 1
    return f"{prefix}-{year}-{count:04d}"


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.String(20), primary_key=True)  # STU-YYYY-XXXX
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100))
    major = db.Column(db.String(100))
    credits_completed = db.Column(db.Integer, default=0)
    gpa = db.Column(db.Float, default=0.0)
    start_semester = db.Column(db.String(20))  # e.g., "Fall"
    start_year = db.Column(db.Integer)
    is_transfer = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(255), nullable=False)
    resume_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship("Application", backref="student", lazy=True)
    coop_records = db.relationship("CoopRecord", backref="student", lazy=True)


class Employer(db.Model):
    __tablename__ = "employers"

    id = db.Column(db.String(20), primary_key=True)  # EMP-YYYY-XXXX
    company_name = db.Column(db.String(150), nullable=False)
    contact_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    location = db.Column(db.String(150))
    website = db.Column(db.String(200))
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    positions = db.relationship("JobPosition", backref="employer", lazy=True)


class Faculty(db.Model):
    __tablename__ = "faculty"

    id = db.Column(db.String(20), primary_key=True)  # FAC-YYYY-XXXX
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(100))
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    coop_records = db.relationship("CoopRecord", backref="faculty", lazy=True)


class JobPosition(db.Model):
    __tablename__ = "job_positions"

    id = db.Column(db.String(20), primary_key=True)  # POS-YYYY-XXXX
    employer_id = db.Column(db.String(20), db.ForeignKey("employers.id"), nullable=False)

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(150))
    weeks = db.Column(db.Integer, default=0)
    hours_per_week = db.Column(db.Integer, default=0)
    total_hours = db.Column(db.Integer, default=0)
    majors_of_interest = db.Column(db.String(255))
    required_skills = db.Column(db.String(255))
    preferred_skills = db.Column(db.String(255))
    salary_info = db.Column(db.String(100))
    status = db.Column(db.String(20), default="Open")  # Open / Pending / Closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship("Application", backref="position", lazy=True)


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), db.ForeignKey("students.id"), nullable=False)
    position_id = db.Column(db.String(20), db.ForeignKey("job_positions.id"), nullable=False)

    status = db.Column(db.String(20), default="Pending")  # Pending / Selected / Rejected / Withdrawn
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    selection = db.relationship("Selection", backref="application", uselist=False)
    eligibility = db.relationship("CoopEligibility", backref="application", uselist=False)
    coop_record = db.relationship("CoopRecord", backref="application", uselist=False)


class Selection(db.Model):
    __tablename__ = "selections"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=False)
    selected_at = db.Column(db.DateTime, default=datetime.utcnow)
    offer_letter_filename = db.Column(db.String(255))


class CoopEligibility(db.Model):
    __tablename__ = "coop_eligibility"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=False)

    is_eligible = db.Column(db.Boolean, default=False)
    gpa_ok = db.Column(db.Boolean, default=False)
    weeks_ok = db.Column(db.Boolean, default=False)
    hours_ok = db.Column(db.Boolean, default=False)
    semesters_ok = db.Column(db.Boolean, default=False)
    checked_at = db.Column(db.DateTime, default=datetime.utcnow)


class CoopRecord(db.Model):
    __tablename__ = "coop_records"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=False)
    student_id = db.Column(db.String(20), db.ForeignKey("students.id"), nullable=False)
    position_id = db.Column(db.String(20), db.ForeignKey("job_positions.id"), nullable=False)

    eligibility_id = db.Column(db.Integer, db.ForeignKey("coop_eligibility.id"))
    faculty_id = db.Column(db.String(20), db.ForeignKey("faculty.id"))

    student_interested = db.Column(db.Boolean, default=False)
    summary_text = db.Column(db.Text)
    summary_status = db.Column(db.String(20), default="Draft")  # Draft / Submitted
    employer_approval = db.Column(db.String(20), default="Pending")  # Pending / Approved / Rejected
    faculty_grade = db.Column(db.String(2))  # A–E
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

