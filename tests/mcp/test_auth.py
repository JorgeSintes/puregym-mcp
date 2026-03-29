import pytest

from puregym_mcp.mcp.auth import StaticTokenVerifier


@pytest.mark.asyncio
async def test_verify_token_valid() -> None:
    """Test that a matching token returns an AccessToken."""
    verifier = StaticTokenVerifier("my-secret-token")
    result = await verifier.verify_token("my-secret-token")

    assert result is not None
    assert result.token == "my-secret-token"
    assert result.client_id == "self"
    assert "puregym" in result.scopes


@pytest.mark.asyncio
async def test_verify_token_invalid() -> None:
    """Test that a non-matching token returns None."""
    verifier = StaticTokenVerifier("my-secret-token")
    result = await verifier.verify_token("wrong-token")

    assert result is None


@pytest.mark.asyncio
async def test_verify_token_none_configured() -> None:
    """Test that no configured token rejects all tokens."""
    verifier = StaticTokenVerifier(None)
    result = await verifier.verify_token("any-token")

    assert result is None


@pytest.mark.asyncio
async def test_verify_token_empty_string() -> None:
    """Test that empty string token behaves correctly."""
    verifier = StaticTokenVerifier("")
    result = await verifier.verify_token("")

    assert result is not None
    assert result.token == ""
