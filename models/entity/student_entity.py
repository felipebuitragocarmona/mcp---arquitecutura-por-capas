from dataclasses import dataclass
from typing import Optional


@dataclass
class StudentEntity:
    id: int
    name: str
    email: str
    age: int
    career: Optional[str] = None
    semester: Optional[int] = None
    resume_path: Optional[str] = None
    created_at: Optional[str] = None
