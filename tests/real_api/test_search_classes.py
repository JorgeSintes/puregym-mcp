"""Tests for authenticated search classes endpoint."""

from datetime import date, datetime, timedelta

import pytest

from puregym_mcp.puregym.api_schemas import ApiDataEnvelope, ApiSearchClass
from puregym_mcp.puregym.client import PureGymClient
from puregym_mcp.puregym.models import GymClass


@pytest.mark.real_api
@pytest.mark.asyncio
async def test_search_classes_authenticated_validates_schema(
    authenticated_client: PureGymClient, sample_center_id: int
):
    """Test that authenticated search response validates against schemas."""

    # Make raw request to validate envelope
    payload = {
        "activities": [],
        "centers": [sample_center_id],
        "endTime": "23:59",
        "id": 0,
        "instructor": "",
        "startTime": "00:00",
        "title": "",
        "weekdays": [0, 1, 2, 3, 4, 5, 6],
    }

    raw_data = await authenticated_client._request_app_json(
        "POST",
        "/bookings/search",
        content_type="application/json; charset=UTF-8",
        json=payload,
    )

    # Validate envelope structure
    envelope = ApiDataEnvelope.model_validate(raw_data)
    assert envelope.status == "success"
    assert isinstance(envelope.data, list)

    # Validate each item as ApiSearchClass
    for i, item in enumerate(envelope.data[:10]):  # Check first 10
        try:
            api_class = ApiSearchClass.model_validate(item)
            # Key fields should be present
            assert api_class.name
            assert api_class.date
            assert api_class.bookingId.booking_id
        except Exception as e:
            pytest.fail(f"ApiSearchClass validation failed for item {i}: {e}")


@pytest.mark.real_api
@pytest.mark.asyncio
async def test_search_classes_authenticated_converts_to_model(
    authenticated_client: PureGymClient, sample_center_id: int
):
    """Test that authenticated search converts to GymClass models."""

    today = datetime.today().strftime("%Y-%m-%d")
    next_week = (datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d")

    classes = await authenticated_client.get_available_classes(
        center_ids=[sample_center_id], from_date=today, to_date=next_week
    )

    assert isinstance(classes, list)

    for i, gym_class in enumerate(classes[:10]):  # Check first 10
        assert isinstance(gym_class, GymClass)
        assert gym_class.date
        assert gym_class.title
        assert gym_class.booking_id
        # Key derived fields
        assert isinstance(gym_class.duration, int)
        if gym_class.center_id is not None:
            assert isinstance(gym_class.center_id, int)


@pytest.mark.real_api
@pytest.mark.asyncio
async def test_search_classes_with_filters(authenticated_client: PureGymClient, sample_center_id: int):
    """Test searching with filters."""

    today = datetime.today().strftime("%Y-%m-%d")
    next_week = (datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d")

    classes = await authenticated_client.get_available_classes(
        center_ids=[sample_center_id],
        from_date=today,
        to_date=next_week,
    )

    assert isinstance(classes, list)
    for gym_class in classes:
        assert isinstance(gym_class, GymClass)
        # All classes should be from the specified center
        assert gym_class.center_id == sample_center_id
        assert date.today() <= date.fromisoformat(f"{gym_class.date}") <= date.today() + timedelta(days=7)
