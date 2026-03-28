"""Tests for authenticated centers endpoints."""

import pytest

from puregym_mcp.puregym.api_schemas import ApiCenterStats, ApiDataEnvelope
from puregym_mcp.puregym.models import CenterLiveStatus, CenterOpeningHours


@pytest.mark.real_api
@pytest.mark.asyncio
async def test_get_center_live_status_validates_schema(authenticated_client, sample_center_id):
    """Test that center live status validates against schemas."""
    # Make raw request to validate envelope
    raw_data = await authenticated_client._request_app_json("GET", f"/centers/stats/{sample_center_id}")

    # Validate envelope structure
    envelope = ApiDataEnvelope.model_validate(raw_data)
    assert envelope.status == "success"
    assert isinstance(envelope.data, dict)
    assert "list" in envelope.data

    # Validate the stats
    stats_data = envelope.data["list"]
    try:
        api_stats = ApiCenterStats.model_validate(stats_data)
        # Key fields should be present
        assert api_stats.centerName or api_stats.webname
        assert api_stats.capacity is not None
        assert api_stats.capacity.people_in_center is not None
        assert api_stats.capacity.max_capacity is not None
    except Exception as e:
        pytest.fail(f"ApiCenterStats validation failed: {e}")


@pytest.mark.real_api
@pytest.mark.asyncio
async def test_get_center_live_status_converts_to_model(authenticated_client, sample_center_id):
    """Test that center live status converts to CenterLiveStatus model."""
    status = await authenticated_client.get_center_live_status(sample_center_id)

    assert isinstance(status, CenterLiveStatus)
    assert status.center_name
    assert status.people_in_center >= 0
    assert status.max_capacity > 0
    assert status.capacity_status
    assert status.opening_hours
    assert isinstance(status.opening_hours, list)

    # Check computed fields
    assert isinstance(status.occupancy_ratio, float)
    assert isinstance(status.is_open_now, (bool, type(None)))
    assert isinstance(status.staffed_now, (bool, type(None)))


@pytest.mark.real_api
@pytest.mark.asyncio
async def test_get_center_open_hours_converts_to_model(authenticated_client, sample_center_id):
    """Test that center open hours converts to CenterOpeningHours models."""
    hours = await authenticated_client.get_center_open_hours(sample_center_id)

    assert isinstance(hours, list)
    assert len(hours) > 0

    for entry in hours:
        assert isinstance(entry, CenterOpeningHours)
        assert entry.name  # Day name like "Mandag"
        assert entry.opening
        assert entry.closing
