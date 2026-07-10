import pytest
from mcp.server import FastMCP

from mcp_server.infrastructure.config import ServerFactory
from tests.conftest import get_tool_names


class TestServerFactory:
    def test_create_returns_fastmcp_instance(self, make_settings):
        factory = ServerFactory.get_instance(make_settings())

        server = factory.create()

        assert isinstance(server, FastMCP)
        assert server.name == "test-server"

    def test_create_registers_ping_tool(self, server):
        assert "ping" in get_tool_names(server)

    def test_singleton_returns_same_instance(self, make_settings):
        settings = make_settings()

        first = ServerFactory.get_instance(settings)
        second = ServerFactory.get_instance(settings)

        assert first is second

    def test_create_registers_jira_auth_tools(self, server):
        tool_names = get_tool_names(server)
        assert "generate_jira_auth_url" in tool_names
        assert "complete_jira_auth" in tool_names

    def test_direct_init_raises(self, make_settings):
        with pytest.raises(TypeError, match="singleton"):
            ServerFactory(make_settings())

    def test_create_token_storage_returns_same_instance(self, make_settings):
        factory = ServerFactory.get_instance(make_settings())

        first = factory._create_token_storage()
        second = factory._create_token_storage()

        assert first is second

    def test_create_registers_sop_resources(self, server):
        resources = server._resource_manager.list_resources()
        templates = server._resource_manager.list_templates()
        assert any(str(r.uri) == "sop://offboardme/sops" for r in resources)
        assert any(t.uri_template == "sop://offboardme/sops/{sop_id}" for t in templates)

    def test_create_registers_dossier_resource(self, server):
        templates = server._resource_manager.list_templates()
        assert any(t.uri_template == "dossier://offboardme/dossiers/{process_id}" for t in templates)

    def test_create_registers_knowledge_graph_resources(self, server):
        templates = server._resource_manager.list_templates()
        assert any(t.uri_template == "kg://offboardme/experts/{topic}" for t in templates)
        assert any(t.uri_template == "kg://offboardme/persons/{person_id}/profile" for t in templates)
