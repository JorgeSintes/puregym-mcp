from datetime import datetime
from types import SimpleNamespace

import pytest

from puregym_mcp.puregym.service import PureGymService


class FakeClient:
    def __init__(self, *, has_credentials: bool, classes=None, bookings=None):
        self.has_credentials = has_credentials
        self.classes = classes or []
        self.bookings = bookings or []
        self.search_calls: list[dict] = []
        self.book_calls: list[tuple[str, int, str]] = []
        self.cancel_calls: list[str] = []

    async def get_all_class_types(self):
        return []

    async def get_all_centers(self):
        return []

    async def get_available_classes(self, **kwargs):
        self.search_calls.append(kwargs)
        return self.classes

    async def get_my_bookings(self):
        return self.bookings

    async def book_by_ids(self, booking_id: str, activity_id: int, payment_type: str):
        self.book_calls.append((booking_id, activity_id, payment_type))
        return {"status": "success", "participationId": "pid-1"}

    async def unbook_participation(self, participation_id: str):
        self.cancel_calls.append(participation_id)
        return {"status": "success"}

    async def aclose(self):
        return None

    async def get_center_live_status(self, center_id: int):
        return {"center_id": center_id}

    async def get_center_open_hours(self, center_id: int):
        return [{"center_id": center_id}]


@pytest.mark.asyncio
async def test_search_classes_uses_anonymous_default_range():
    client = FakeClient(has_credentials=False)
    service = PureGymService(client)  # type: ignore[arg-type]

    await service.search_classes()

    call = client.search_calls[0]
    assert call["from_date"] is not None
    assert (datetime.fromisoformat(call["to_date"]) - datetime.fromisoformat(call["from_date"])).days == 14


def test_default_search_window_respects_auth_mode():
    anonymous = PureGymService(FakeClient(has_credentials=False))  # type: ignore[arg-type]
    authenticated = PureGymService(FakeClient(has_credentials=True))  # type: ignore[arg-type]
    now = datetime(2026, 3, 20, 12, 0)

    anonymous_window = anonymous.default_search_window(now)
    authenticated_window = authenticated.default_search_window(now)

    assert anonymous_window.from_date == "2026-03-20"
    assert anonymous_window.to_date == "2026-04-03"
    assert authenticated_window.to_date == "2026-04-17"


@pytest.mark.asyncio
async def test_book_and_cancel_require_authenticated_mode():
    service = PureGymService(FakeClient(has_credentials=False))  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="Authenticated PureGym credentials"):
        await service.book_class("b-1", 11, "membership")

    with pytest.raises(ValueError, match="Authenticated PureGym credentials"):
        await service.cancel_booking("pid-1")


@pytest.mark.asyncio
async def test_book_and_cancel_delegate_to_client():
    client = FakeClient(has_credentials=True)
    service = PureGymService(client)  # type: ignore[arg-type]

    booked = await service.book_class("b-1", 11, "membership")
    cancelled = await service.cancel_booking("pid-1")

    assert booked["status"] == "success"
    assert cancelled["status"] == "success"
    assert client.book_calls == [("b-1", 11, "membership")]
    assert client.cancel_calls == ["pid-1"]


@pytest.mark.asyncio
async def test_list_my_bookings_uses_dashboard_bookings():
    bookings = [SimpleNamespace(date="2026-03-23")]
    client = FakeClient(has_credentials=True, bookings=bookings)
    service = PureGymService(client)  # type: ignore[arg-type]

    result = await service.list_my_bookings(from_date="2026-03-20", to_date="2026-03-30")

    assert result == bookings


@pytest.mark.asyncio
async def test_center_status_tools_require_authenticated_mode():
    service = PureGymService(FakeClient(has_credentials=False))  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="Authenticated PureGym credentials"):
        await service.get_center_live_status(123)

    with pytest.raises(ValueError, match="Authenticated PureGym credentials"):
        await service.get_center_open_hours(123)
