import json
from pathlib import Path
from typing import Iterable, Dict, Any, List, Optional

from .repository_interface import StudentRepositoryInterface


JSON_FILE = Path("students.json")


class StudentRepositoryJSON(StudentRepositoryInterface):
    def __init__(self, file_path: str | Path = JSON_FILE) -> None:
        self.file = Path(file_path)

    def load_all(self) -> List[Dict[str, Any]]:
        if self.file.exists():
            with open(self.file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    # Interface: get_all / insert / update / get_by_id / delete
    def get_all(self) -> List[Dict[str, Any]]:
        return self.load_all()

    def insert(self, student: Dict[str, Any]) -> None:
        students = self.load_all()
        students.append(student)
        self.save_all(students)

    def save_all(self, students: Iterable[Dict[str, Any]]) -> None:
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(list(students), f, indent=2, ensure_ascii=False)

    def get_by_id(self, student_id: int) -> Optional[Dict[str, Any]]:
        students = self.load_all()
        for s in students:
            if s.get("id") == student_id:
                return s
        return None

    def update(self, student_id: int, new_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        students = self.load_all()
        for i, s in enumerate(students):
            if s.get("id") == student_id:
                updated = {**s, **new_data}
                updated["id"] = student_id
                if "created_at" not in updated:
                    updated["created_at"] = s.get("created_at")
                students[i] = updated
                self.save_all(students)
                return updated
        return None

    def delete(self, student_id: int) -> bool:
        students = self.load_all()
        new_students = [s for s in students if s.get("id") != student_id]
        if len(new_students) == len(students):
            return False
        self.save_all(new_students)
        return True
