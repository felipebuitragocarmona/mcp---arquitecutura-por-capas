from fastmcp import FastMCP
from business.student_service import StudentService
from models.dto.student_dto import StudentCreate, StudentUpdate
from data.repository_factory import get_repository

mcp = FastMCP("students")

# Obtener la implementación de repositorio según la configuración (.env)
repo = get_repository()

service = StudentService(repo=repo)


@mcp.tool()
async def add_student(
    name: str,
    email: str,
    age: int,
    career: str,
    semester: int
):
    """
    Registers a new student in the academic system.

    Parameters:
        name (str): Full name of the student.
        email (str): Student's personal or institutional email address.
        age (int): Student's age.
        career (str): Academic program or career name.
        semester (int): Current semester the student is enrolled in.

    Returns:
        dict | object:
            - Registered student information if successful.
            - A dictionary containing the error message and exception type if an error occurs.

    Usage:
        Use this tool to create and store a new student through the service layer.
    """
    try:
        student = StudentCreate(
            name=name,
            email=email,
            age=age,
            career=career,
            semester=semester,
        )
        return service.add_student(student)
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def list_students():
    """
    Retrieve all registered students.

    Returns:
        List containing all students stored in the system.
    """
    return service.list_students()


@mcp.tool()
async def get_stats():
    """
    Retrieve statistics about the student database.

    Includes:
        - Total number of students
        - Average student age

    Returns:
        Dictionary containing database statistics.
    """
    return service.get_stats()


@mcp.tool()
async def update_student(
    student_id: int,
    name: str | None = None,
    email: str | None = None,
    age: int | None = None,
    career: str | None = None,
    semester: int | None = None,
  ):
    """
    Update an existing student with partial data.

    Parameters:
      student_id (int): Identifier of the student to update.
      name (str | None): New full name.
      email (str | None): New email address.
      age (int | None): New age.
      career (str | None): New academic career.
      semester (int | None): New semester.

    Returns:
      Updated student information or an error dictionary.
    """
    try:
      payload = {
        "name": name,
        "email": email,
        "age": age,
        "career": career,
        "semester": semester,
      }
      payload = {k: v for k, v in payload.items() if v is not None}
      if not payload:
        return {"error": "No se enviaron campos para actualizar"}

      student_update = StudentUpdate(**payload)
      return service.update_student(student_id, student_update)
    except Exception as e:
      return {"error": str(e), "type": type(e).__name__}


@mcp.tool()
async def delete_student(student_id: int):
    """
    Delete a student by id.

    Parameters:
      student_id (int): Identifier of the student to delete.

    Returns:
      Dictionary indicating deletion status or error details.
    """
    try:
      return service.delete_student(student_id)
    except Exception as e:
      return {"error": str(e), "type": type(e).__name__}

@mcp.tool()
async def get_version():
    """
    Retrieve the current version of the academic system service.

    Returns:
        str: Current application version.
    """
    return "1.0.1"

@mcp.tool()
def dashboard() -> str:
    """Genera un dashboard HTML con notas, asistencia y evolución histórica."""

    html = """
            <!DOCTYPE html>
            <html>
            <head>
              <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
              <style>
                body  { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
                .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
                .card { background: white; border-radius: 8px; padding: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
              </style>
            </head>
            <body>
              <h2>Dashboard Académico</h2>
              <div class="grid">
                <div class="card"><canvas id="notas"></canvas></div>
                <div class="card"><canvas id="asistencia"></canvas></div>
                <div class="card" style="grid-column: span 2"><canvas id="historial"></canvas></div>
              </div>
              <script>
                new Chart(document.getElementById("notas"), {
                  type: "bar",
                  data: {
                    labels: ["Cálculo","Física","Prog.","Inglés","Estadística"],
                    datasets: [{ label: "Notas", data: [3.8,4.2,4.9,3.5,4.1],
                      backgroundColor: "rgba(54,162,235,0.7)" }]
                  },
                  options: { plugins: { title: { display: true, text: "Notas por Materia" }},
                             scales: { y: { min: 0, max: 5 }}}
                });
            
                new Chart(document.getElementById("asistencia"), {
                  type: "doughnut",
                  data: {
                    labels: ["Asistió","Faltó"],
                    datasets: [{ data: [88, 12],
                      backgroundColor: ["rgba(75,192,192,0.7)","rgba(255,99,132,0.7)"] }]
                  },
                  options: { plugins: { title: { display: true, text: "Asistencia Global (%)" }}}
                });
            
                new Chart(document.getElementById("historial"), {
                  type: "line",
                  data: {
                    labels: ["2023-1","2023-2","2024-1","2024-2","2025-1"],
                    datasets: [{ label: "Promedio Semestral", data: [3.4,3.6,3.5,3.9,4.1],
                      borderColor: "rgba(153,102,255,1)", tension: 0.3, fill: false }]
                  },
                  options: { plugins: { title: { display: true, text: "Evolución Histórica" }},
                             scales: { y: { min: 2.5, max: 5 }}}
                });
              </script>
            </body>
            </html>
            """
    return html