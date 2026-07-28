from fastapi import APIRouter
from typing import List
from business.student_service import StudentService
from models.dto.student_dto import Student, StudentCreate, StudentUpdate
from pydantic import BaseModel
from data.repository_factory import get_repository

router = APIRouter()
# Crear servicio con repositorio elegido por la fábrica (env REPO_TYPE)
service = StudentService(repo=get_repository())


class AdvancedQueryRequest(BaseModel):
    pregunta: str


@router.post("/students", response_model=Student)
def create_student(data: StudentCreate):
    return service.add_student(data)


@router.get("/students", response_model=List[Student])
def list_students():
    return service.list_students()


@router.get("/students/stats")
def stats():
    return service.get_stats()


@router.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int):
    student = service.get_student(student_id)
    if not student:
        return {"error": "Estudiante no encontrado"}
    return student


@router.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, data: StudentUpdate):
    return service.update_student(student_id, data)


@router.delete("/students/{student_id}")
def delete_student(student_id: int):
    return service.delete_student(student_id)


@router.get("/students/schema")
def students_schema():
    return service.get_students_schema()


@router.get("/students/schema/toon")
def students_schema_toon():
    return {"schema_toon": service.get_students_schema_toon()}


@router.post("/students/advanced-query")
def advanced_query(data: AdvancedQueryRequest):
    return service.run_advanced_query(data.pregunta)


@router.post("/students/generate-sql")
def generate_sql(data: AdvancedQueryRequest):
    return service.generate_sql_with_gemini(data.pregunta)
