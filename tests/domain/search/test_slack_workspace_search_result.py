from mcp_server.domain.search.slack_workspace_search_result import SlackWorkspaceSearchResult


class TestFromApiItemMessages:
    def test_maps_message_fields(self):
        item = {"text": "deploy failed again", "permalink": "https://x/archives/C1/p1", "ts": "1700000000.000100"}

        result = SlackWorkspaceSearchResult.from_api_item("messages", item)

        assert result.content_type == "messages"
        assert result.text == "deploy failed again"
        assert result.permalink == "https://x/archives/C1/p1"
        assert result.timestamp == "1700000000.000100"


class TestFromApiItemFiles:
    def test_maps_file_fields(self):
        item = {"title": "runbook.pdf", "permalink": "https://x/files/f1"}

        result = SlackWorkspaceSearchResult.from_api_item("files", item)

        assert result.content_type == "files"
        assert result.text == "runbook.pdf"
        assert result.permalink == "https://x/files/f1"


class TestFromApiItemChannels:
    def test_maps_channel_fields(self):
        item = {"name": "incidents", "id": "C123"}

        result = SlackWorkspaceSearchResult.from_api_item("channels", item)

        assert result.content_type == "channels"
        assert result.text == "incidents"


class TestFromApiItemUsers:
    def test_prefers_real_name_over_name(self):
        item = {"real_name": "Jane Doe", "name": "jane"}

        result = SlackWorkspaceSearchResult.from_api_item("users", item)

        assert result.text == "Jane Doe"

    def test_falls_back_to_name_when_no_real_name(self):
        item = {"name": "jane"}

        result = SlackWorkspaceSearchResult.from_api_item("users", item)

        assert result.text == "jane"


class TestFromApiItemUnknownContentType:
    def test_missing_fields_default_to_empty(self):
        result = SlackWorkspaceSearchResult.from_api_item("unknown", {})

        assert result.text == ""
        assert result.permalink is None
        assert result.timestamp is None
