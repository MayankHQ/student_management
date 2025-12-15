from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from enum import Enum

from database import Base


# ---------------- User Role ----------------
class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"


# ---------------- User ----------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)

    student = relationship("Student", back_populates="user", uselist=False)


# ---------------- Student ----------------
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    roll_no = Column(String(50), unique=True, nullable=False)

    user = relationship("User", back_populates="student")
    marks = relationship("Marks", back_populates="student", uselist=False)


# ---------------- Marks (FIXED 5 SUBJECTS) ----------------
class Marks(Base):
    __tablename__ = "marks"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), unique=True)

    s1 = Column(Integer, nullable=False)
    s2 = Column(Integer, nullable=False)
    s3 = Column(Integer, nullable=False)
    s4 = Column(Integer, nullable=False)
    s5 = Column(Integer, nullable=False)

    student = relationship("Student", back_populates="marks")
