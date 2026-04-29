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
    created_at: Optional[str] = None
