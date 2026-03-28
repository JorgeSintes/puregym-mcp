"""Fixtures for real API integration tests.

These tests run against the live PureGym API and require credentials.
Set PUREGYM_USERNAME and PUREGYM_PASSWORD environment variables.
"""

import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio

from puregym_mcp.puregym.client import PureGymClient


@pytest.fixture(scope="module")
def credentials() -> dict[str, str | None]:
    """Get PureGym credentials from environment."""
    username = os.environ.get("PUREGYM_USERNAME")
    password = os.environ.get("PUREGYM_PASSWORD")
    return {"username": username, "password": password}


@pytest.fixture(scope="module")
def has_credentials(credentials: dict[str, str | None]) -> bool:
    """Check if credentials are configured."""
    return bool(credentials["username"] and credentials["password"])


@pytest_asyncio.fixture
async def authenticated_client(
    credentials: dict[str, str | None], has_credentials: bool
) -> AsyncGenerator[PureGymClient, None]:
    """Create an authenticated client.

    Skips the test if credentials are not configured.
    Uses a longer timeout for real API tests.
    """
    if not has_credentials:
        pytest.skip("PUREGYM_USERNAME and PUREGYM_PASSWORD not set")

    # Use 30 second timeout for real API tests
    client = PureGymClient(
        username=credentials["username"],
        password=credentials["password"],
        timeout=30.0,
    )
    yield client
    await client.aclose()


@pytest_asyncio.fixture
async def anonymous_client() -> AsyncGenerator[PureGymClient, None]:
    """Create an anonymous client (no credentials).

    Uses a longer timeout for real API tests.
    """
    # Use 30 second timeout for real API tests
    client = PureGymClient(timeout=30.0)
    yield client
    await client.aclose()


@pytest_asyncio.fixture
async def sample_center_id(authenticated_client: PureGymClient, has_credentials: bool) -> int:
    """Get a sample center ID from the authenticated centers endpoint.

    Skips the test if credentials are not configured or no centers are found.
    """
    if not has_credentials:
        pytest.skip("PUREGYM_USERNAME and PUREGYM_PASSWORD not set")

    centers = await authenticated_client.get_all_centers()
    for group in centers:
        if group.options:
            return group.options[0].value
    pytest.skip("No centers found in API response")


@pytest_asyncio.fixture
async def sample_center_id_anonymous(anonymous_client) -> int:
    """Get a sample center ID from the anonymous centers endpoint.

    Skips the test if no centers are found.
    """
    centers = await anonymous_client.get_all_centers()
    for group in centers:
        if group.options:
            return group.options[0].value
    pytest.skip("No centers found in API response")
