from mcp_server.infrastructure.config.server_factory import ServerFactory
from mcp_server.infrastructure.config.settings import McpServerSettings


class Application:
    def __init__(self) -> None:
        self._settings = McpServerSettings()

    def run(self) -> None:
        factory = ServerFactory.get_instance(self._settings)
        server = factory.create()
        server.run(transport="streamable-http")


def main():
    Application().run()


if __name__ == "__main__":
    main()
