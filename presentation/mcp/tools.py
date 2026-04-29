from fastmcp import FastMCP
from business.student_service import StudentService
from models.dto.student_dto import StudentCreate
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
async def get_version():
    """
    Retrieve the current version of the academic system service.

    Returns:
        str: Current application version.
    """
    return "2.0.5"