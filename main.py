from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

import models
import schemas
from database import SessionLocal, engine
from security import hash_password, verify_password
from jwt_utils import create_access_token, verify_access_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from models import User, Student, Marks, UserRole


# ---------------- Create Tables ----------------
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
security = HTTPBearer()


# ---------------- DB Dependency ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- Auth Dependency ----------------
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    payload = verify_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# ---------------- Root ----------------
@app.get("/")
def root():
    return "Student Management System API"


# ---------------- Register ----------------
@app.post("/register")
def register(user: schemas.UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = User(
        username=user.username,
        password=hash_password(user.password),
        role=user.role.value
    )

    db.add(new_user)
    db.commit()

    return {"message": f"{user.role.value.capitalize()} registered successfully"}


# ---------------- Login ----------------
@app.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        data={"sub": db_user.username, "role": db_user.role}
    )

    return {"access_token": token, "token_type": "bearer"}


# ---------------- Me ----------------
@app.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "role": current_user.role
    }

# ---------------- Student: View Profile ----------------
@app.get("/students/me")
def student_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.STUDENT.value:
        raise HTTPException(status_code=403, detail="Only students allowed")

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="Profile not created yet")

    return {
        "username": current_user.username,
        "roll_no": student.roll_no
    }

# ---------------- Teacher: Assign Roll + Marks (ONE STEP) ----------------
@app.post("/marks")
def assign_marks(
    data: schemas.AssignMarks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.TEACHER.value:
        raise HTTPException(status_code=403, detail="Only teachers allowed")

    # 1. ensure student profile exists
    student = db.query(Student).filter(
        Student.user_id == data.user_id
    ).first()

    if not student:
        student = Student(
            user_id=data.user_id,
            roll_no=data.roll_no
        )
        db.add(student)
        db.flush()
    else:
        student.roll_no = data.roll_no  # allow update

    # 2. save/update marks
    marks = db.query(Marks).filter(
        Marks.student_id == student.id
    ).first()

    if not marks:
        marks = Marks(
            student_id=student.id,
            s1=data.s1,
            s2=data.s2,
            s3=data.s3,
            s4=data.s4,
            s5=data.s5
        )
        db.add(marks)
    else:
        marks.s1 = data.s1
        marks.s2 = data.s2
        marks.s3 = data.s3
        marks.s4 = data.s4
        marks.s5 = data.s5

    db.commit()
    return {"message": "Roll number and marks saved successfully"}


# ---------------- Student: View Own Marks ----------------
@app.get("/students/marks", response_model=schemas.StudentMarksOut)
def view_my_marks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.STUDENT.value:
        raise HTTPException(status_code=403, detail="Only students allowed")

    student = db.query(Student).filter(
        Student.user_id == current_user.id
    ).first()

    if not student or not student.marks:
        raise HTTPException(status_code=404, detail="Marks not assigned yet")

    m = student.marks
    total = m.s1 + m.s2 + m.s3 + m.s4 + m.s5

    return {
        "s1": m.s1,
        "s2": m.s2,
        "s3": m.s3,
        "s4": m.s4,
        "s5": m.s5,
        "total": total
    }


# ---------------- Leaderboard ----------------
@app.get("/leaderboard", response_model=list[schemas.LeaderboardOut])
def leaderboard(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user)
):
    results = (
        db.query(
            Student.roll_no,
            User.username,
            Marks.s1,
            Marks.s2,
            Marks.s3,
            Marks.s4,
            Marks.s5
        )
        .join(User, User.id == Student.user_id)
        .join(Marks, Marks.student_id == Student.id)
        .all()
    )

    leaderboard = []
    for r in results:
        total = r.s1 + r.s2 + r.s3 + r.s4 + r.s5
        leaderboard.append({
            "roll_no": r.roll_no,
            "student": r.username,
            "total": total
        })

    leaderboard.sort(key=lambda x: x["total"], reverse=True)

    for idx, entry in enumerate(leaderboard, start=1):
        entry["rank"] = idx

    return leaderboard


# ---------------- Teacher: List Student Users ----------------
@app.get("/students/users")
def list_student_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.TEACHER.value:
        raise HTTPException(status_code=403, detail="Only teachers allowed")

    return db.query(User).filter(
        User.role == UserRole.STUDENT.value
    ).all()
