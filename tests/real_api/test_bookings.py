"""Tests for authenticated bookings endpoint."""

import pytest

from puregym_mcp.puregym.api_schemas import ApiBookedClass, ApiDataEnvelope
from puregym_mcp.puregym.models import GymClass


@pytest.mark.real_api
@pytest.mark.asyncio
async def test_get_my_bookings_validates_schema(authenticated_client):
    """Test that bookings response validates against schemas."""
    # Make raw request to validate envelope
    raw_data = await authenticated_client._request_app_json("GET", "/bookings")

    # Validate envelope structure
    envelope = ApiDataEnvelope.model_validate(raw_data)
    assert envelope.status == "success"
    assert isinstance(envelope.data, list)

    # Validate each item as ApiBookedClass
    for i, item in enumerate(envelope.data[:10]):  # Check first 10
        try:
            api_booking = ApiBookedClass.model_validate(item)
            # Key fields should be present
            assert api_booking.booking.name
            assert api_booking.booking.date
        except Exception as e:
            pytest.fail(f"ApiBookedClass validation failed for item {i}: {e}")


@pytest.mark.real_api
@pytest.mark.asyncio
async def test_get_my_bookings_converts_to_model(authenticated_client):
    """Test that bookings convert to GymClass models."""
    bookings = await authenticated_client.get_my_bookings()

    assert isinstance(bookings, list)

    for i, booking in enumerate(bookings[:10]):  # Check first 10
        assert isinstance(booking, GymClass)
        assert booking.date
        assert booking.title
        assert booking.booking_id
        # Bookings should have a state
        assert booking.state is not None
        # Should have participation_id for bookings
        if booking.participation_id:
            assert isinstance(booking.participation_id, str)
