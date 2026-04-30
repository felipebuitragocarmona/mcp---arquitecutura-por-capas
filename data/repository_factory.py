import os
import logging
from abc import ABC, abstractmethod
from dotenv import load_dotenv

from .repository_interface import StudentRepositoryInterface
from .student_repository_sqlite import StudentRepositorySQLite
from .student_repository_json import StudentRepositoryJSON

# Cargar variables del archivo .env
load_dotenv()

# No configurar handlers aquí; la configuración va en el entrypoint
logger = logging.getLogger(__name__)


class RepositoryFactory(ABC):
    """Creator abstracto — contrato obligatorio para subclases."""

    @abstractmethod
    def create_repository(self) -> StudentRepositoryInterface:
        ... # Método que debe implementar cada factory concreta para retornar su repositorio específico.


class SQLiteRepositoryFactory(RepositoryFactory):
    def __init__(self, path: str | None = None):
        self.path = path or os.getenv("SQLITE_PATH", "students.db")

    def create_repository(self) -> StudentRepositoryInterface:
        logger.info("Creating SQLite repository -> %s", self.path)
        return StudentRepositorySQLite(self.path)


class JSONRepositoryFactory(RepositoryFactory):
    def __init__(self, path: str | None = None):
        self.path = path or os.getenv("JSON_PATH", "students.json")

    def create_repository(self) -> StudentRepositoryInterface:
        logger.info("Creating JSON repository -> %s", self.path)
        return StudentRepositoryJSON(self.path)


# Registro de factories disponibles — agregar uno nuevo no toca lógica existente
FACTORIES: dict[str, type[RepositoryFactory]] = {
    "sqlite": SQLiteRepositoryFactory,
    "json": JSONRepositoryFactory,
}


def get_factory(repo_type: str | None = None) -> RepositoryFactory:
    """Retorna el factory correspondiente al tipo solicitado.

    No realiza `if/else` — usa `FACTORIES` para facilitar extensibilidad.
    """

    key = (repo_type or os.getenv("REPO_TYPE", "sqlite")).lower()
    factory_class = FACTORIES.get(key)

    if factory_class is None:
        raise ValueError(f"Unknown REPO_TYPE '{key}'. Available: {list(FACTORIES)}")

    return factory_class()


def get_repository() -> StudentRepositoryInterface:
    """Compatibilidad: crea y devuelve el repositorio por defecto."""
    factory = get_factory()
    return factory.create_repository()