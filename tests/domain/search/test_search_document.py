from mcp_server.domain.search.search_document import SearchDocument

_SAMPLE_SOP = {
    "id": "11111111-1111-1111-1111-111111111111",
    "content": "Restart the deploy pipeline\nStep 1: check logs\nStep 2: retry job",
    "author": "U12345",
    "tags": ["deploy", "pipeline"],
    "origin_channel": "C67890",
    "version": 2,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-03-05T10:30:00Z",
}


class TestSearchDocumentFromSop:
    def test_uses_first_line_as_title(self):
        doc = SearchDocument.from_sop(_SAMPLE_SOP, base_url="https://app.example.com/sops")

        assert doc.title == "Restart the deploy pipeline"

    def test_maps_core_fields(self):
        doc = SearchDocument.from_sop(_SAMPLE_SOP, base_url="https://app.example.com/sops")

        assert doc.external_id == "11111111-1111-1111-1111-111111111111"
        assert doc.content == _SAMPLE_SOP["content"]
        assert doc.author == "U12345"
        assert doc.tags == ["deploy", "pipeline"]
        assert doc.origin_channel == "C67890"

    def test_builds_link_from_base_url_and_id(self):
        doc = SearchDocument.from_sop(_SAMPLE_SOP, base_url="https://app.example.com/sops")

        assert doc.link == "https://app.example.com/sops/11111111-1111-1111-1111-111111111111"

    def test_date_updated_is_date_only(self):
        doc = SearchDocument.from_sop(_SAMPLE_SOP, base_url="https://app.example.com/sops")

        assert doc.date_updated == "2026-03-05"

    def test_truncates_long_single_line_title_to_80_chars(self):
        long_content = "x" * 200
        sop = {**_SAMPLE_SOP, "content": long_content}

        doc = SearchDocument.from_sop(sop, base_url="https://app.example.com/sops")

        assert doc.title == "x" * 80
        assert doc.description == long_content[:200]

    def test_description_is_content_snippet(self):
        doc = SearchDocument.from_sop(_SAMPLE_SOP, base_url="https://app.example.com/sops")

        assert doc.description.startswith("Restart the deploy pipeline")

    def test_uses_explicit_title_when_present(self):
        sop = {**_SAMPLE_SOP, "title": "Deploy pipeline recovery"}

        doc = SearchDocument.from_sop(sop, base_url="https://app.example.com/sops")

        assert doc.title == "Deploy pipeline recovery"

    def test_falls_back_to_first_line_when_title_missing(self):
        doc = SearchDocument.from_sop(_SAMPLE_SOP, base_url="https://app.example.com/sops")

        assert doc.title == "Restart the deploy pipeline"

    def test_falls_back_to_first_line_when_title_empty(self):
        sop = {**_SAMPLE_SOP, "title": ""}

        doc = SearchDocument.from_sop(sop, base_url="https://app.example.com/sops")

        assert doc.title == "Restart the deploy pipeline"

    def test_truncates_explicit_title_to_80_chars(self):
        sop = {**_SAMPLE_SOP, "title": "x" * 200}

        doc = SearchDocument.from_sop(sop, base_url="https://app.example.com/sops")

        assert doc.title == "x" * 80
