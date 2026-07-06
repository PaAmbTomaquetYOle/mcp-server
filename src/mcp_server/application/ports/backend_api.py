from abc import ABC, abstractmethod


class IBackendApiPort(ABC):
    """
    Interface for the Backend API Port.
    """

    @abstractmethod
    async def get_dossier_by_process(self, process_id: str) -> dict:
        """
        Retrieve a specific dossier from the backend API by its associated Process ID.
        """

    @abstractmethod
    async def search_dossiers(
        self, employee_name: str | None = None, process_id: str | None = None
    ) -> list[dict]:
        """
        Search dossiers from the backend API by employee name and/or process ID.
        At least one of the two filters must be provided.
        """