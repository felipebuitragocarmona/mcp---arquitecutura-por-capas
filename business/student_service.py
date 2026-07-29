import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Sequence

import httpx

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
        print("Tipo de repositorio ",type(repo))
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
            resume_path=data.get("resume_path"),
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
            "resume_path": entity.resume_path,
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
            resume_path=None,
            created_at=now,
        )
        students.append(self._to_dict(entity))
        # Persistir usando la implementación inyectada
        self.repo.insert(self._to_dict(entity))
        return StudentDTO(**self._to_dict(entity))

    def list_students(self) -> List[StudentDTO]:
        print("Listando estudiantes con el repo")
        print(type(self.repo))
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
        data = update.model_dump(exclude_unset=True) if hasattr(update, "model_dump") else update.dict(exclude_unset=True)
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

    def upload_student_resume_bytes(self, student_id: int, pdf_bytes: bytes, filename: str) -> Dict[str, Any]:
        try:
            student_id = int(student_id)
        except Exception:
            return {"error": "ID inválido"}

        if not pdf_bytes:
            return {"error": "El archivo está vacío"}

        student = self.repo.get_by_id(student_id)
        if not student:
            return {"error": f"Estudiante {student_id} no encontrado"}

        extension = Path(filename).suffix.lower() if filename else ""
        if extension != ".pdf":
            return {"error": "La hoja de vida debe estar en formato PDF"}

        resumes_dir = Path("uploads") / "resumes"
        resumes_dir.mkdir(parents=True, exist_ok=True)

        file_path = resumes_dir / f"student_{student_id}{extension}"
        file_path.write_bytes(pdf_bytes)

        relative_path = file_path.as_posix()
        updated = self.repo.update(student_id, {"resume_path": relative_path})
        if not updated:
            return {"error": "No fue posible guardar la ruta de la hoja de vida"}

        return {
            "status": "ok",
            "student_id": student_id,
            "ruta_guardada": relative_path,
            "tamaño_bytes": len(pdf_bytes),
        }

    def get_students_schema(self) -> Dict[str, Any]:
        columns = self._get_repo_columns()
        return {"table": "students", "columns": columns}

    def get_students_schema_toon(self) -> str:
        schema = self.get_students_schema()
        columns = schema["columns"]
        column_names = ",".join(col["name"] for col in columns)
        column_types = ",".join(col["type"] for col in columns)
        nullable_flags = ",".join("1" if col.get("nullable") else "0" for col in columns)
        defaults = ",".join("" if col.get("default") is None else str(col.get("default")) for col in columns)
        return (
            f'{schema["table"]}[{len(columns)}]{{name,type,nullable,default}}:\n'
            f'{column_names}\n'
            f'{column_types}\n'
            f'{nullable_flags}\n'
            f'{defaults}'
        )

    def _get_repo_columns(self) -> List[Dict[str, Any]]:
        if hasattr(self.repo, "get_table_columns"):
            columns = self.repo.get_table_columns()
            if columns:
                return columns

        students = self.repo.get_all()
        keys: List[str] = []
        seen = set()
        for student in students:
            for key in student.keys():
                if key not in seen:
                    seen.add(key)
                    keys.append(key)

        columns: List[Dict[str, Any]] = []
        for key in keys:
            sample_value = next((student.get(key) for student in students if key in student), None)
            columns.append({
                "name": key,
                "type": self._infer_value_type(sample_value),
                "nullable": sample_value is None,
                "default": None,
            })

        return columns

    def _infer_value_type(self, value: Any) -> str:
        if isinstance(value, bool):
            return "bool"
        if isinstance(value, int):
            return "int"
        if isinstance(value, float):
            return "float"
        if isinstance(value, dict):
            return "object"
        if isinstance(value, list):
            return "array"
        if value is None:
            return "null"
        return "str"

    def execute_advanced_sql(self, sql: str, params: Sequence[Any] | None = None) -> Dict[str, Any]:
        if not hasattr(self.repo, "execute_sql"):
            return {"error": "El repositorio actual no soporta ejecución SQL directa"}

        if not self._is_safe_select_sql(sql):
            return {"error": "La consulta generada no pasó la validación de seguridad"}

        print(f"[consultas_avanzadas] SQL generada: {sql}")
        rows = self.repo.execute_sql(sql, params=params)
        return {"sql": sql, "rows": rows, "count": len(rows)}

    def generate_sql_with_gemini(self, user_question: str) -> Dict[str, Any]:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {"error": "Falta la variable de entorno GEMINI_API_KEY"}

        model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash").strip()
        if model.startswith("models/"):
            model = model.removeprefix("models/")
        schema_toon = self.get_students_schema_toon()
        prompt = self._build_gemini_prompt(user_question, schema_toon)
        print("[consultas_avanzadas] Prompt enviado a Gemini:")
        print(prompt)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        with httpx.Client(timeout=60.0) as client:
            try:
                response = client.post(
                    url,
                    headers={"x-goog-api-key": api_key},
                    json={
                        "contents": [
                            {
                                "role": "user",
                                "parts": [{"text": prompt}],
                            }
                        ],
                        "generationConfig": {
                            "temperature": 0,
                            "maxOutputTokens": 512,
                        },
                    },
                )
                response.raise_for_status()
                payload = response.json()
            except httpx.HTTPStatusError as exc:
                return self._gemini_http_error(exc.response, model)
            except httpx.RequestError as exc:
                return {
                    "error": "No fue posible conectar con la API de Gemini",
                    "detail": str(exc),
                }
            except ValueError:
                return {"error": "Gemini devolvió una respuesta que no es JSON válido"}

        try:
            sql = self._extract_sql_from_gemini_response(payload)
        except (KeyError, TypeError, ValueError) as exc:
            return {"error": str(exc)}
        return {"schema_toon": schema_toon, "sql": sql, "raw": payload}

    def _gemini_http_error(self, response: httpx.Response, model: str) -> Dict[str, Any]:
        detail = response.reason_phrase
        try:
            payload = response.json()
            api_error = payload.get("error", {})
            detail = api_error.get("message") or detail
        except ValueError:
            pass

        message = f"Gemini rechazó la solicitud (HTTP {response.status_code})"
        if response.status_code == 404:
            message = f"El modelo Gemini '{model}' no está disponible para esta clave"

        return {
            "error": message,
            "detail": detail,
            "status_code": response.status_code,
        }

    def run_advanced_query(self, user_question: str) -> Dict[str, Any]:
        generated = self.generate_sql_with_gemini(user_question)
        if "error" in generated:
            return generated
        return self.execute_advanced_sql(generated["sql"])

    def _build_gemini_prompt(self, user_question: str, schema_toon: str) -> str:
        return f"""
Eres un generador de SQL para SQLite.

Debes responder SOLO con una consulta SQL válida y segura.

Reglas:
- Usa únicamente la tabla `students`.
- Solo se permite `SELECT` o `WITH`.
- No uses punto y coma.
- No uses `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `CREATE`, `REPLACE`, `ATTACH` ni `PRAGMA`.
- Si la pregunta no se puede resolver con los campos disponibles, genera la mejor consulta posible sobre la tabla.

Estructura de la tabla en TOON:
```toon
{schema_toon}
```

Pregunta del usuario:
{user_question}
""".strip()

    def _extract_sql_from_gemini_response(self, payload: Dict[str, Any]) -> str:
        candidates = payload.get("candidates") or []
        if not candidates:
            raise ValueError("Gemini no devolvió candidatos")

        content = candidates[0].get("content") or {}
        parts = content.get("parts") or []
        text = "".join(part.get("text", "") for part in parts).strip()
        if not text:
            raise ValueError("Gemini devolvió una respuesta vacía")

        text = text.strip().strip("`")
        if text.lower().startswith("sql"):
            text = text[3:].strip().lstrip(":").strip()

        normalized = re.sub(r"\s+", " ", text).strip()
        return normalized

    def _is_safe_select_sql(self, sql: str) -> bool:
        normalized = " ".join(sql.strip().lower().split())
        blocked = (";", "insert ", "update ", "delete ", "drop ", "alter ", "create ", "replace ", "attach ", "pragma ")
        return normalized.startswith(("select ", "with ")) and not any(token in normalized for token in blocked)
