from abc import ABC, abstractmethod
from uuid import UUID


class IBackendApiPort(ABC):
    """
    Interface for the Backend API Port.
    """

    @abstractmethod
    async def get_dossier_by_id(self, dossier_id: UUID) -> dict:
        """
        Retrieve a specific dossier from the backend API by its ID.
        """

    @abstractmethod
    async def get_dossier_by_process(self, process_id: UUID) -> dict:
        """
        Retrieve a specific dossier from the backend API by its associated Process ID.
        """