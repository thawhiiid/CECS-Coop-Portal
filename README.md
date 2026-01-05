# CECS-Coop-Portal 
Full-Stack Co-op Automation & Management System

A full-stack web application designed to automate and manage the university co-op process for students, employers, and faculty coordinators. This system streamlines internship applications, eligibility evaluation, co-op summaries, and grading workflows using role-based access and automated decision logic.

---

## 🚀 Project Overview

This project was developed as part of **CIS 425 (Database & Information Systems)** and simulates a real-world academic co-op management portal. The goal was to replace manual, paper-based workflows with a centralized, automated, and database-driven system.

The platform supports **three user roles**:
- **Students** – apply for internships, view eligibility, submit co-op summaries
- **Employers** – post positions, review applicants, select candidates, approve summaries
- **Faculty Coordinators** – manage co-op students by department and assign grades

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite (SQLAlchemy ORM)
- **Frontend:** HTML, CSS (Jinja templates)
- **Authentication:** Role-based login with hashed passwords
- **Architecture:** MVC-style routing with REST-style endpoints

---

## ✨ Key Features

### 🔐 Role-Based Authentication
- Secure login system for **students, employers, and faculty**
- Password hashing and session management
- **100% unique ID generation** for users and job postings

### 📄 Internship & Application Management
- Employers can create and manage multiple job postings
- Students can search and apply to internships
- Real-time tracking of application status (Pending, Selected, Rejected)

### ⚙️ Automated Eligibility Engine
- Automatic co-op eligibility evaluation based on:
  - GPA (≥ 2.0)
  - Internship duration (≥ 7 weeks)
  - Total work hours (≥ 140 hours)
- Eligibility results stored and displayed transparently

### 📬 Automated Workflow & Notifications
- System automatically updates statuses when actions occur
- Eligible selected students receive automated email notifications (simulated)
- Students can indicate interest in co-op credit directly in the portal

### 🧑‍🏫 Faculty Coordination & Grading
- **One faculty coordinator per department**
- Faculty can only view students from their own department
- Review submitted co-op summaries and assign grades

### 📊 Dynamic Dashboards
- Student, employer, and faculty dashboards with real-time data
- Database-driven views for applications, summaries, and approvals

---

## 🧠 Database Design

- Normalized relational schema using SQLAlchemy models
- Core entities include:
  - Students, Employers, Faculty
  - Job Positions
  - Applications
  - Eligibility Records
  - Co-op Records (summaries & grades)
- Enforced relationships and role-based data visibility

---

## ▶️ How to Run Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/coop-management-system.git
   cd coop-management-system
