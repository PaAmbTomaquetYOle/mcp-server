from mcp_server.domain.search import TokenNormalizer


class TestTokenSet:
    def test_stems_plural_to_singular(self):
        normalizer = TokenNormalizer()

        assert normalizer.token_set("deploys") == normalizer.token_set("deploy")

    def test_stems_conjugation(self):
        normalizer = TokenNormalizer()

        assert normalizer.token_set("running") == normalizer.token_set("run")

    def test_is_case_insensitive(self):
        normalizer = TokenNormalizer()

        assert normalizer.token_set("Onboarding") == normalizer.token_set("onboard")

    def test_tokenizes_multiple_words(self):
        normalizer = TokenNormalizer()

        tokens = normalizer.token_set("Restart deploy pipeline")

        assert tokens == {"restart", "deploy", "pipelin"}

    def test_empty_text_yields_no_tokens(self):
        normalizer = TokenNormalizer()

        assert normalizer.token_set("") == set()
