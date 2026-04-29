from pydantic import BaseModel, EmailStr
from typing import Optional


class StudentBase(BaseModel):
    name: str
    email: EmailStr
    age: int
    career: Optional[str] = None
    semester: Optional[int] = None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    career: Optional[str] = None
    semester: Optional[int] = None


class Student(StudentBase):
    id: int
    created_at: str

    class Config:
        orm_mode = True
