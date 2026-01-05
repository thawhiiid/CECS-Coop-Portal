# app.py
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

from models import (
    db, Student, Employer, Faculty,
    JobPosition, Application, Selection,
    CoopEligibility, CoopRecord, generate_id
)

# ---------- App and DB setup ----------

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "coop_portal.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Create tables once at startup (Flask 3 safe)
with app.app_context():
    db.create_all()


# ---------- Helpers ----------

def current_user():
    """Return (role, user_obj) for the logged-in user, or (None, None)."""
    role = session.get("role")
    user_id = session.get("user_id")
    if not role or not user_id:
        return None, None

    if role == "student":
        user = Student.query.get(user_id)
    elif role == "employer":
        user = Employer.query.get(user_id)
    elif role == "faculty":
        user = Faculty.query.get(user_id)
    else:
        user = None
    return role, user


def check_eligibility(student: Student, position: JobPosition):
    """
    This function checks if a student is eligible for co-op based on:
    - Their GPA
    - The number of weeks the internship runs
    - The total number of hours
    - Whether they have enough semesters completed (very simplified)
    """

    # Student must have at least a 2.0 GPA
    gpa_ok = student.gpa is not None and student.gpa >= 2.0

    # Internship must run for at least 7 weeks
    weeks_ok = position.weeks is not None and position.weeks >= 7

    # Calculate total hours:
    # If total_hours is already stored, use it.
    # If not, calculate it using weeks * hours per week.
    hours = position.total_hours or 0
    if not hours and position.weeks and position.hours_per_week:
        hours = position.weeks * position.hours_per_week

    # Student must complete at least 140 total hours
    hours_ok = hours >= 140

    # Check if student has completed required semesters.
    # This is just a placeholder logic — can be expanded later.
    if student.is_transfer:
        # For transfer students, make sure start_year exists
        semesters_ok = student.start_year is not None
    else:
        # For regular students, same simple check
        semesters_ok = student.start_year is not None

    # Student is eligible ONLY if all conditions are True
    is_eligible = gpa_ok and weeks_ok and hours_ok and semesters_ok

    # Return the full breakdown so we know why they passed/failed
    return is_eligible, gpa_ok, weeks_ok, hours_ok, semesters_ok


def send_email(to_email: str, subject: str, body: str):
    """
    Fake email sender for this project.
    In a real system, this would use SMTP. Here we just print to console.
    """
    print("========== EMAIL SENT ==========")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print("Body:")
    print(body)
    print("================================")


# ---------- Auth Routes ----------

@app.route("/")
def index():
    if "role" in session:
        role, _ = current_user()
        if role == "student":
            return redirect(url_for("student_dashboard"))
        if role == "employer":
            return redirect(url_for("employer_dashboard"))
        if role == "faculty":
            return redirect(url_for("faculty_dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role")  # student/employer/faculty
        email = request.form.get("email")
        password = request.form.get("password")

        user = None
        if role == "student":
            user = Student.query.filter_by(email=email).first()
        elif role == "employer":
            user = Employer.query.filter_by(email=email).first()
        elif role == "faculty":
            user = Faculty.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session["role"] = role
            session["user_id"] = user.id
            flash("Logged in successfully.", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ---------- Registration Routes ----------

@app.route("/register/student", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        department = request.form.get("department")
        major = request.form.get("major")
        credits = int(request.form.get("credits") or 0)
        gpa = float(request.form.get("gpa") or 0)
        start_semester = request.form.get("start_semester")
        start_year = int(request.form.get("start_year") or 0)
        is_transfer = bool(request.form.get("is_transfer"))
        password = request.form.get("password")

        if Student.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("register_student"))

        student_id = generate_id("STU", Student)
        student = Student(
            id=student_id,
            name=name,
            email=email,
            phone=phone,
            department=department,
            major=major,
            credits_completed=credits,
            gpa=gpa,
            start_semester=start_semester,
            start_year=start_year,
            is_transfer=is_transfer,
            password_hash=generate_password_hash(password)
        )
        db.session.add(student)
        db.session.commit()
        flash("Student registered. You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register_student.html")


@app.route("/register/employer", methods=["GET", "POST"])
def register_employer():
    if request.method == "POST":
        company_name = request.form.get("company_name")
        contact_name = request.form.get("contact_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        location = request.form.get("location")
        website = request.form.get("website")
        password = request.form.get("password")

        if Employer.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("register_employer"))

        employer_id = generate_id("EMP", Employer)
        employer = Employer(
            id=employer_id,
            company_name=company_name,
            contact_name=contact_name,
            email=email,
            phone=phone,
            location=location,
            website=website,
            password_hash=generate_password_hash(password)
        )
        db.session.add(employer)
        db.session.commit()
        flash("Employer registered. You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register_employer.html")


@app.route("/register/faculty", methods=["GET", "POST"])
def register_faculty():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        department = request.form.get("department")
        password = request.form.get("password")

        # One coordinator per department
        existing_dept = Faculty.query.filter_by(department=department).first()
        if existing_dept:
            flash("A co-op coordinator already exists for this department.", "danger")
            return redirect(url_for("register_faculty"))

        if Faculty.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("register_faculty"))

        faculty_id = generate_id("FAC", Faculty)
        faculty = Faculty(
            id=faculty_id,
            name=name,
            email=email,
            department=department,
            password_hash=generate_password_hash(password)
        )
        db.session.add(faculty)
        db.session.commit()
        flash("Faculty registered. You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register_faculty.html")


# ---------- Student Routes ----------

@app.route("/student/dashboard")
def student_dashboard():
    role, user = current_user()
    if role != "student":
        return redirect(url_for("login"))

    applications = Application.query.filter_by(student_id=user.id).all()
    total_apps = len(applications)
    pending_apps = len([a for a in applications if a.status == "Pending"])

    # Simple eligibility summary: if any application is eligible
    eligibilities = CoopEligibility.query.join(Application).filter(
        Application.student_id == user.id,
        CoopEligibility.is_eligible == True  # noqa: E712
    ).all()
    eligible_flag = "Yes" if eligibilities else "No"

    return render_template(
        "student_dashboard.html",
        student=user,
        total_apps=total_apps,
        pending_apps=pending_apps,
        eligible_flag=eligible_flag,
        applications=applications,
    )


@app.route("/student/search")
def student_search():
    role, user = current_user()
    if role != "student":
        return redirect(url_for("login"))

    q = request.args.get("q", "")
    employer_name = request.args.get("employer", "")
    location = request.args.get("location", "")

    query = JobPosition.query.filter(
        (JobPosition.status == "Open") | (JobPosition.status.is_(None))
    )
    if q:
        query = query.filter(JobPosition.title.ilike(f"%{q}%"))
    if employer_name:
        query = query.join(Employer).filter(Employer.company_name.ilike(f"%{employer_name}%"))
    if location:
        query = query.filter(JobPosition.location.ilike(f"%{location}%"))

    positions = query.order_by(JobPosition.created_at.desc()).all()
    return render_template("search_jobs.html", positions=positions, q=q,
                           employer_name=employer_name, location=location)


@app.route("/position/<position_id>")
def job_details(position_id):
    role, user = current_user()
    position = JobPosition.query.get_or_404(position_id)

    existing_app = None
    if role == "student" and user:
        existing_app = Application.query.filter_by(student_id=user.id, position_id=position.id).first()

    return render_template("job_details.html", position=position, existing_app=existing_app)


@app.route("/apply/<position_id>", methods=["POST"])
def apply_to_position(position_id):
    role, user = current_user()
    if role != "student":
        return redirect(url_for("login"))

    position = JobPosition.query.get_or_404(position_id)
    existing = Application.query.filter_by(student_id=user.id, position_id=position.id).first()
    if existing:
        flash("You already applied to this position.", "info")
        return redirect(url_for("job_details", position_id=position_id))

    app_obj = Application(student_id=user.id, position_id=position.id, status="Pending")
    db.session.add(app_obj)
    db.session.commit()
    flash("Application submitted.", "success")
    return redirect(url_for("student_applications"))


@app.route("/student/applications")
def student_applications():
    role, user = current_user()
    if role != "student":
        return redirect(url_for("login"))

    applications = Application.query.filter_by(student_id=user.id).order_by(
        Application.applied_at.desc()
    ).all()
    return render_template("student_applications.html", applications=applications)


@app.route("/student/application/<int:app_id>/withdraw", methods=["POST"])
def withdraw_application(app_id):
    role, user = current_user()
    if role != "student":
        return redirect(url_for("login"))

    app_obj = Application.query.get_or_404(app_id)
    if app_obj.student_id != user.id:
        return redirect(url_for("student_applications"))

    app_obj.status = "Withdrawn"
    db.session.commit()
    flash("Application withdrawn.", "info")
    return redirect(url_for("student_applications"))


@app.route("/student/application/<int:app_id>/interest", methods=["POST"])
def indicate_interest(app_id):
    """Eligible student indicates they want co-op credit."""
    role, user = current_user()
    if role != "student":
        return redirect(url_for("login"))

    app_obj = Application.query.get_or_404(app_id)
    if app_obj.student_id != user.id:
        return redirect(url_for("student_applications"))

    if not app_obj.eligibility or not app_obj.eligibility.is_eligible:
        flash("You are not marked as eligible for co-op for this position.", "danger")
        return redirect(url_for("student_applications"))

    coop_record = app_obj.coop_record
    if not coop_record:
        coop_record = CoopRecord(
            application_id=app_obj.id,
            student_id=user.id,
            position_id=app_obj.position_id,
            eligibility_id=app_obj.eligibility.id,
        )
        db.session.add(coop_record)

    coop_record.student_interested = True
    coop_record.updated_at = datetime.utcnow()
    db.session.commit()

    flash("Your interest in co-op credit has been recorded.", "success")
    return redirect(url_for("student_applications"))


@app.route("/student/summary/<int:app_id>", methods=["GET", "POST"])
def submit_summary(app_id):
    role, user = current_user()
    if role != "student":
        return redirect(url_for("login"))

    application = Application.query.get_or_404(app_id)
    if application.student_id != user.id:
        return redirect(url_for("student_applications"))

    coop_record = application.coop_record
    if not coop_record:
        coop_record = CoopRecord(
            application_id=application.id,
            student_id=user.id,
            position_id=application.position_id,
            eligibility_id=getattr(application.eligibility, "id", None),
            student_interested=True,
        )
        db.session.add(coop_record)
        db.session.commit()

    if request.method == "POST":
        summary = request.form.get("summary")
        action = request.form.get("action")  # draft or submit
        coop_record.summary_text = summary
        if action == "submit":
            coop_record.summary_status = "Submitted"
        else:
            coop_record.summary_status = "Draft"
        coop_record.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Summary saved.", "success")
        return redirect(url_for("student_applications"))

    return render_template("submit_summary.html", application=application, coop_record=coop_record)


# ---------- Employer Routes ----------

@app.route("/employer/dashboard")
def employer_dashboard():
    role, user = current_user()
    if role != "employer":
        return redirect(url_for("login"))

    positions = JobPosition.query.filter_by(employer_id=user.id).all()

    # Active postings: treat None or "Open" as active, not closed
    active_count = len([
        p for p in positions
        if p.status in (None, "", "Open")
    ])
    total_apps = 0
    selected_count = 0
    pending_reviews = 0

    for p in positions:
        total_apps += len(p.applications)
        for a in p.applications:
            if a.status == "Selected":
                selected_count += 1
                if a.coop_record and a.coop_record.employer_approval == "Pending":
                    pending_reviews += 1

    return render_template(
        "employer_dashboard.html",
        employer=user,
        positions=positions,
        active_count=active_count,
        total_apps=total_apps,
        selected_count=selected_count,
        pending_reviews=pending_reviews,
    )


@app.route("/employer/post", methods=["POST"])
def employer_post():
    """Create a new job posting (form at bottom of employer_dashboard)."""
    role, user = current_user()
    if role != "employer":
        return redirect(url_for("login"))

    title = request.form.get("title")
    description = request.form.get("description")
    location = request.form.get("location")
    weeks = int(request.form.get("weeks") or 0)
    hours_per_week = int(request.form.get("hours_per_week") or 0)
    total_hours = weeks * hours_per_week
    majors_of_interest = request.form.get("majors_of_interest")
    required_skills = request.form.get("required_skills")
    preferred_skills = request.form.get("preferred_skills")
    salary_info = request.form.get("salary_info")

    position_id = generate_id("POS", JobPosition)
    position = JobPosition(
        id=position_id,
        employer_id=user.id,
        title=title,
        description=description,
        location=location,
        weeks=weeks,
        hours_per_week=hours_per_week,
        total_hours=total_hours,
        majors_of_interest=majors_of_interest,
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        salary_info=salary_info,
        status="Open",
    )
    db.session.add(position)
    db.session.commit()
    flash("Job position created.", "success")
    return redirect(url_for("employer_dashboard"))


@app.route("/employer/position/<position_id>/applicants")
def employer_applicants(position_id):
    role, user = current_user()
    if role != "employer":
        return redirect(url_for("login"))

    position = JobPosition.query.get_or_404(position_id)
    if position.employer_id != user.id:
        return redirect(url_for("employer_dashboard"))

    return render_template("employer_applicants.html", position=position)


@app.route("/employer/application/<int:app_id>/select", methods=["POST"])
def employer_select(app_id):
    role, user = current_user()
    if role != "employer":
        return redirect(url_for("login"))

    application = Application.query.get_or_404(app_id)
    position = application.position
    student = application.student

    application.status = "Selected"
    position.status = "Pending"

    selection = Selection(application_id=application.id)
    db.session.add(selection)

    is_eligible, gpa_ok, weeks_ok, hours_ok, semesters_ok = check_eligibility(student, position)
    eligibility = CoopEligibility(
        application_id=application.id,
        is_eligible=is_eligible,
        gpa_ok=gpa_ok,
        weeks_ok=weeks_ok,
        hours_ok=hours_ok,
        semesters_ok=semesters_ok,
    )
    db.session.add(eligibility)
    db.session.commit()

    # Email notification for eligible students
    if is_eligible:
        subject = "CECS Co-op Portal: You have been selected and are eligible"
        body = (
            f"Hello {student.name},\n\n"
            f"You have been selected for the position '{position.title}' at {position.employer.company_name}.\n"
            f"Our records show you meet the eligibility requirements for co-op credit.\n\n"
            f"If you are interested in receiving co-op credit, please log in to the portal and indicate your interest.\n\n"
            f"- CECS Co-op Portal"
        )
        send_email(student.email, subject, body)

    flash(f"Candidate selected. Eligibility result: {'Eligible' if is_eligible else 'Not eligible'}.", "info")
    return redirect(url_for("employer_applicants", position_id=position.id))


@app.route("/employer/application/<int:app_id>/reject", methods=["POST"])
def employer_reject(app_id):
    role, user = current_user()
    if role != "employer":
        return redirect(url_for("login"))

    application = Application.query.get_or_404(app_id)
    application.status = "Rejected"
    db.session.commit()
    flash("Application rejected.", "info")
    return redirect(url_for("employer_applicants", position_id=application.position_id))


@app.route("/employer/pending-reviews")
def employer_pending_reviews():
    """List co-op records where student has submitted summary but employer has not approved yet."""
    role, user = current_user()
    if role != "employer":
        return redirect(url_for("login"))

    coop_records = (
        CoopRecord.query
        .join(Application)
        .join(JobPosition)
        .filter(
            JobPosition.employer_id == user.id,
            CoopRecord.summary_status == "Submitted",
            CoopRecord.employer_approval == "Pending",
        )
        .all()
    )
    return render_template("employer_pending_reviews.html", coop_records=coop_records)


@app.route("/employer/coop/<int:coop_id>", methods=["GET", "POST"])
def employer_review_summary(coop_id):
    role, user = current_user()
    if role != "employer":
        return redirect(url_for("login"))

    coop_record = CoopRecord.query.get_or_404(coop_id)
    application = coop_record.application
    position = application.position
    if position.employer_id != user.id:
        return redirect(url_for("employer_dashboard"))

    if request.method == "POST":
        decision = request.form.get("approval")  # Approved / Rejected
        coop_record.employer_approval = decision
        coop_record.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Co-op summary review submitted.", "success")
        return redirect(url_for("employer_pending_reviews"))

    return render_template("employer_review_summary.html", coop_record=coop_record)


# ---------- Faculty Routes ----------

@app.route("/faculty/dashboard")
def faculty_dashboard():
    role, user = current_user()
    if role != "faculty":
        return redirect(url_for("login"))

    # Only see co-op students in this faculty's department
    coop_records = (
        CoopRecord.query
        .join(Student)
        .filter(Student.department == user.department)
        .all()
    )

    total_students = len({cr.student_id for cr in coop_records})
    pending_summaries = len([
        cr for cr in coop_records
        if cr.summary_status == "Submitted" and not cr.faculty_grade
    ])
    graded = len([cr for cr in coop_records if cr.faculty_grade])
    awaiting_approval = len([
        cr for cr in coop_records if cr.employer_approval == "Pending"
    ])

    return render_template(
        "faculty_students.html",
        faculty=user,
        coop_records=coop_records,
        total_students=total_students,
        pending_summaries=pending_summaries,
        graded=graded,
        awaiting_approval=awaiting_approval,
    )


@app.route("/faculty/grade/<int:coop_id>", methods=["GET", "POST"])
def faculty_grade(coop_id):
    role, user = current_user()
    if role != "faculty":
        return redirect(url_for("login"))

    coop_record = CoopRecord.query.get_or_404(coop_id)

    if request.method == "POST":
        grade = request.form.get("grade")
        coop_record.faculty_grade = grade
        coop_record.faculty_id = user.id
        coop_record.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Grade saved.", "success")
        return redirect(url_for("faculty_dashboard"))

    return render_template("faculty_grade.html", coop_record=coop_record)


# ---------- Run ----------

if __name__ == "__main__":
    app.run(debug=True)
