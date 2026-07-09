from abc import ABC, abstractmethod

from mcp.server import FastMCP


class BaseController(ABC):
    """Base controller abstract class that all specific controllers should inherit from. It provides a common structure and enforces the implementation of the register method for adding tools, resources, or prompts to the MCP server."""
    
    _server: FastMCP

    def __init__(self, server: FastMCP) -> None:
        self._server = server

    @abstractmethod
    def register(self) -> None:
        """
        Register the controller's tools, resources or prompts with the MCP server. This method should be implemented by all subclasses to add their specific tools, resources or prompts to the server.
        """
