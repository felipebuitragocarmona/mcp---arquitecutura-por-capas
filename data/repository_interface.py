from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional, List, Dict, Sequence, Tuple


class StudentRepositoryInterface(ABC):
    @abstractmethod
    def get_all(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def insert(self, student: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def get_by_id(self, student_id: int) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def update(self, student_id: int, new_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def delete(self, student_id: int) -> bool:
        pass

    def execute_sql(self, sql: str, params: Sequence[Any] | None = None) -> List[Dict[str, Any]]:
        raise NotImplementedError
