"""Tests for read-only endpoints (work without authentication)."""

import pytest

from puregym_mcp.puregym.client import PureGymClient
from puregym_mcp.puregym.models import (
    CenterGroup,
    GymClassTypesGroup,
)


@pytest.mark.real_api
@pytest.mark.asyncio
async def test_get_all_class_types(anonymous_client: PureGymClient):
    """Test fetching all class types without authentication."""
    class_types = await anonymous_client.get_all_class_types()

    assert isinstance(class_types, list)
    assert len(class_types) > 0
    for group in class_types:
        assert isinstance(group, GymClassTypesGroup)
        assert group.title
        assert isinstance(group.options, list)


@pytest.mark.real_api
@pytest.mark.asyncio
async def test_get_all_centers(anonymous_client):
    """Test fetching all centers without authentication."""
    centers = await anonymous_client.get_all_centers()

    assert isinstance(centers, list)
    assert len(centers) > 0
    for group in centers:
        assert isinstance(group, CenterGroup)
        assert group.label
        assert isinstance(group.options, list)


@pytest.mark.real_api
@pytest.mark.asyncio
async def test_get_available_classes_anonymous(anonymous_client):
    """Test searching classes without authentication.

    Uses specific class IDs to minimize API load while keeping 7-day window.
    """
    from datetime import datetime, timedelta

    today = datetime.today().strftime("%Y-%m-%d")
    next_week = (datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d")

    classes = await anonymous_client.get_available_classes(
        class_ids=[34941, 23742],
        from_date=today,
        to_date=next_week,
    )

    assert isinstance(classes, list)
    # Classes may be empty, but if present they should be valid
    for gym_class in classes:
        assert gym_class.date
        assert gym_class.title
        assert gym_class.booking_id
