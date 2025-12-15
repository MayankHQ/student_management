🎓 Student Management System (Backend-Focused)

A role-based Student Management System built with FastAPI, PostgreSQL, and JWT authentication.
The project is intentionally backend-focused, with a minimal Streamlit UI used only to interact with and validate backend functionality.

🚀 Features
🔐 Authentication & Authorization

JWT-based authentication

Role-based access control (teacher / student)

Secure protected APIs

👩‍🏫 Teacher Capabilities

Register and log in as a teacher

View all registered students

Assign roll number and marks (fixed 5 subjects) in a single atomic operation

Update marks anytime

View global leaderboard

👨‍🎓 Student Capabilities

Register and log in as a student

View assigned roll number

View marks and total score

View leaderboard and rank

🏆 Leaderboard

Ranks students by total marks

Displays:

Rank

Roll Number

Student Username

Total Marks

🧠 Design Decisions
Fixed Subjects

Subjects are fixed (S1–S5) and not dynamically managed.
This was a deliberate design choice to:

reduce unnecessary complexity

focus on backend correctness

avoid over-engineering

No Separate Teacher Table

Teachers are represented as users with a teacher role.
A separate Teacher table was avoided since teachers do not hold domain data in the current scope.

Backend-First Approach

The Streamlit UI is intentionally simple.
The primary focus of this project is:

backend architecture

domain modeling

data consistency

authorization logic

🧱 Tech Stack

Backend: FastAPI

Database: PostgreSQL

ORM: SQLAlchemy

Auth: JWT (python-jose)

UI: Streamlit (minimal, for testing)

Environment: Python virtual environment

📁 Project Structure
project-root/
├── main.py              # FastAPI routes and business logic
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── database.py          # DB connection and session
├── jwt_utils.py         # JWT creation & verification
├── security.py          # Password hashing
├── streamlit_app.py     # Minimal UI for interaction
├── requirements.txt
├── .env.example
└── README.md

▶️ How to Run
1️⃣ Install dependencies
pip install -r requirements.txt

2️⃣ Set environment variables

Create .env from .env.example and set:

DATABASE_URL

SECRET_KEY

3️⃣ Start backend
uvicorn main:app --reload

4️⃣ Start UI
streamlit run streamlit_app.py

📌 Notes

UI is intentionally kept simple

Project is designed to be easily extended (subjects, classes, teacher ownership, etc.)

Focus is on clean backend engineering practices

🧩 Possible Extensions

Dynamic subject management

Class / batch grouping

Pagination and filtering

Unit tests

Deployment (Docker / Cloud)

📄 License

This project is for learning and demonstration purposes.
