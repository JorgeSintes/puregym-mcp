from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from puregym_mcp.puregym.client import PureGymClient
from puregym_mcp.puregym.filters import filter_by_booked
from puregym_mcp.puregym.schemas import CenterGroup, GymClass, GymClassTypesGroup


@dataclass(frozen=True)
class SearchDefaults:
    from_date: str
    to_date: str


class PureGymService:
    def __init__(self, client: PureGymClient):
        self.client = client

    @property
    def is_authenticated(self) -> bool:
        return self.client.has_credentials

    def default_search_window(self, now: datetime | None = None) -> SearchDefaults:
        now = now or datetime.today()
        search_days_allowed = 28 if self.is_authenticated else 14
        return SearchDefaults(
            from_date=now.strftime("%Y-%m-%d"),
            to_date=(now + timedelta(days=search_days_allowed)).strftime("%Y-%m-%d"),
        )

    async def list_class_types(self) -> list[GymClassTypesGroup]:
        return await self.client.get_all_class_types()

    async def list_centers(self) -> list[CenterGroup]:
        return await self.client.get_all_centers()

    async def search_classes(
        self,
        class_ids: list[int] | None = None,
        center_ids: list[int] | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> list[GymClass]:
        defaults = self.default_search_window()
        return await self.client.get_available_classes(
            class_ids=class_ids,
            center_ids=center_ids,
            from_date=from_date or defaults.from_date,
            to_date=to_date or defaults.to_date,
        )

    async def list_my_bookings(
        self,
        class_ids: list[int] | None = None,
        center_ids: list[int] | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> list[GymClass]:
        if not self.is_authenticated:
            raise ValueError("Authenticated PureGym credentials are required to list bookings")

        if class_ids is None:
            class_ids = [option.value for group in await self.list_class_types() for option in group.options]
        if center_ids is None:
            center_ids = [option.value for group in await self.list_centers() for option in group.options]

        classes = await self.search_classes(
            class_ids=class_ids,
            center_ids=center_ids,
            from_date=from_date,
            to_date=to_date,
        )
        return filter_by_booked(classes)

    async def book_class(self, booking_id: str, activity_id: int, payment_type: str) -> dict:
        if not self.is_authenticated:
            raise ValueError("Authenticated PureGym credentials are required to create bookings")
        return await self.client.book_by_ids(booking_id, activity_id, payment_type)

    async def cancel_booking(self, participation_id: str) -> dict:
        if not self.is_authenticated:
            raise ValueError("Authenticated PureGym credentials are required to cancel bookings")
        return await self.client.unbook_participation(participation_id)

    async def aclose(self) -> None:
        await self.client.aclose()
