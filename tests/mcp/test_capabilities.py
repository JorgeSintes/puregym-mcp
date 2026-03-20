from puregym_mcp.mcp.capabilities import get_capabilities


def test_capabilities_are_anonymous_without_credentials(monkeypatch):
    monkeypatch.delenv("PUREGYM_USERNAME", raising=False)
    monkeypatch.delenv("PUREGYM_PASSWORD", raising=False)

    capabilities = get_capabilities()

    assert capabilities.authenticated is False
    assert capabilities.search_days_allowed == 14


def test_capabilities_are_authenticated_with_credentials(monkeypatch):
    monkeypatch.setenv("PUREGYM_USERNAME", "user")
    monkeypatch.setenv("PUREGYM_PASSWORD", "pass")

    capabilities = get_capabilities()

    assert capabilities.authenticated is True
    assert capabilities.search_days_allowed == 28
