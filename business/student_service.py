from datetime import datetime
from typing import List, Optional, Dict, Any

from data.repository_interface import StudentRepositoryInterface
from data.student_repository_sqlite import StudentRepositorySQLite
from models.entity.student_entity import StudentEntity
from models.dto.student_dto import Student as StudentDTO, StudentCreate, StudentUpdate


class StudentService:
    """Servicio para operaciones CRUD sobre estudiantes.

    Opera sobre la implementación de repositorio inyectada (`StudentRepositoryInterface`).
    """

    def __init__(self, repo: StudentRepositoryInterface | None = None) -> None:
        # Inyectar la implementación de persistencia (SQLite por defecto)
        self.repo: StudentRepositoryInterface = repo if repo is not None else StudentRepositorySQLite()

    def _next_id(self, students: List[Dict[str, Any]]) -> int:
        if not students:
            return 1
        try:
            return max(int(s.get("id", 0)) for s in students) + 1
        except Exception:
            return len(students) + 1

    def _to_entity(self, data: Dict[str, Any]) -> StudentEntity:
        return StudentEntity(
            id=int(data.get("id")),
            name=data.get("name"),
            email=data.get("email"),
            age=int(data.get("age")),
            career=data.get("career"),
            semester=data.get("semester"),
            created_at=data.get("created_at"),
        )

    def _to_dict(self, entity: StudentEntity) -> Dict[str, Any]:
        return {
            "id": entity.id,
            "name": entity.name,
            "email": entity.email,
            "age": entity.age,
            "career": entity.career,
            "semester": entity.semester,
            "created_at": entity.created_at,
        }

    def add_student(self, student: StudentCreate) -> StudentDTO:
        students = self.repo.get_all()
        if any(s.get("email") == student.email for s in students):
            return {"error": "Email ya registrado"}  # type: ignore

        new_id = self._next_id(students)
        now = datetime.now().isoformat()
        entity = StudentEntity(
            id=new_id,
            name=student.name,
            email=student.email,
            age=student.age,
            career=student.career,
            semester=student.semester,
            created_at=now,
        )
        students.append(self._to_dict(entity))
        # Persistir usando la implementación inyectada
        self.repo.insert(self._to_dict(entity))
        return StudentDTO(**self._to_dict(entity))

    def list_students(self) -> List[StudentDTO]:
        return [StudentDTO(**s) for s in self.repo.get_all()]

    def get_stats(self) -> Dict[str, Any]:
        students = self.repo.get_all()
        total = len(students)
        if total == 0:
            return {"total": 0}
        avg = sum(int(s.get("age", 0)) for s in students) / total
        return {"total": total, "average_age": round(avg, 2)}

    def get_student(self, student_id: int) -> Optional[StudentDTO]:
        try:
            student_id = int(student_id)
        except Exception:
            return None
        s = self.repo.get_by_id(student_id)
        if not s:
            return None
        return StudentDTO(**s)

    def update_student(self, student_id: int, update: StudentUpdate) -> Dict[str, Any] | StudentDTO:
        try:
            student_id = int(student_id)
        except Exception:
            return {"error": "ID inválido"}
        data = update.dict(exclude_unset=True)
        students = self.repo.get_all()
        # validar email único si se intenta cambiar
        if "email" in data:
            if any(s.get("email") == data.get("email") and int(s.get("id", 0)) != student_id for s in students):
                return {"error": "Email ya registrado"}

        updated = self.repo.update(student_id, data)
        if not updated:
            return {"error": "Estudiante no encontrado"}
        return StudentDTO(**updated)

    def delete_student(self, student_id: int) -> Dict[str, Any]:
        try:
            student_id = int(student_id)
        except Exception:
            return {"error": "ID inválido"}

        ok = self.repo.delete(student_id)
        if not ok:
            return {"error": "Estudiante no encontrado"}
        return {"deleted": True}
