from pydantic import BaseModel, Field
from enum import Enum


# ---------------- Auth ----------------
class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class RegisterRole(str, Enum):
    student = "student"
    teacher = "teacher"


class UserRegister(BaseModel):
    username: str
    password: str
    role: RegisterRole


# ---------------- Teacher → Assign Marks ----------------
class AssignMarks(BaseModel):
    user_id: int                    # student user id
    roll_no: str                    # assigned once (can be updated)
    s1: int = Field(..., ge=0, le=100)
    s2: int = Field(..., ge=0, le=100)
    s3: int = Field(..., ge=0, le=100)
    s4: int = Field(..., ge=0, le=100)
    s5: int = Field(..., ge=0, le=100)


# ---------------- Student Views ----------------
class StudentProfileOut(BaseModel):
    roll_no: str

    class Config:
        from_attributes = True


class StudentMarksOut(BaseModel):
    s1: int
    s2: int
    s3: int
    s4: int
    s5: int
    total: int


# ---------------- Leaderboard ----------------
class LeaderboardOut(BaseModel):
    rank: int
    roll_no: str
    student: str
    total: int
