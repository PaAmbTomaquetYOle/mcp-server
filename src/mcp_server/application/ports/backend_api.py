from abc import ABC, abstractmethod


class IBackendApiPort(ABC):
    """
    Interface for the Backend API Port.
    """

    @abstractmethod
    async def search_dossiers(
        self, employee_name: str | None = None, process_id: str | None = None
    ) -> list[dict]:
        """
        Search dossiers from the backend API by employee name and/or process ID.
        At least one of the two filters must be provided.
        """

    @abstractmethod
    async def search_sops(
        self,
        text: str | None = None,
        tags: list[str] | None = None,
        page: int = 1,
        size: int = 20,
    ) -> dict:
        """
        Search SOPs from the backend API by free text and/or tags, paginated.

        Returns the raw paginated response: items, page, size, total, total_pages.
        """

    @abstractmethod
    async def get_sop(self, sop_id: str) -> dict:
        """
        Retrieve a single SOP from the backend API by its ID.
        """