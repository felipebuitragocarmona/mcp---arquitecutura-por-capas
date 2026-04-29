import os
from dotenv import load_dotenv

from .repository_interface import StudentRepositoryInterface
from .student_repository_sqlite import StudentRepositorySQLite
from .student_repository_json import StudentRepositoryJSON

# Cargar variables del archivo .env
load_dotenv()


def get_repository() -> StudentRepositoryInterface:
    """
    Returns a StudentRepositoryInterface implementation based on
    environment variables loaded from .env

    Supported variables:
        REPO_TYPE   : sqlite (default) | json
        SQLITE_PATH : SQLite database path
        JSON_PATH   : JSON file path
    """

    repo_type = os.getenv("REPO_TYPE", "sqlite").lower()

    print("=" * 40)
    print("Repository Factory")
    print(f"REPO_TYPE loaded: {repo_type}")
    print("=" * 40)

    if repo_type == "json":
        json_path = os.getenv("JSON_PATH", "students.json")

        print(f"Using JSON Repository -> {json_path}")
        return StudentRepositoryJSON(json_path)

    sqlite_path = os.getenv("SQLITE_PATH", "students.db")

    print(f"Using SQLite Repository -> {sqlite_path}")

    return StudentRepositorySQLite(sqlite_path)