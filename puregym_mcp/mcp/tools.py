from __future__ import annotations

from puregym_mcp.puregym.service import PureGymService


def register_tools(mcp, service: PureGymService) -> None:
    @mcp.tool()
    async def get_capabilities() -> dict:
        """Return server capabilities and the current PureGym search window."""
        return {
            "authenticated": service.is_authenticated,
            "search_days_allowed": 28 if service.is_authenticated else 14,
        }

    @mcp.tool()
    async def list_class_types() -> list[dict]:
        """List available PureGym class types grouped the same way as the site."""
        groups = await service.list_class_types()
        return [group.model_dump(mode="json") for group in groups]

    @mcp.tool()
    async def list_centers() -> list[dict]:
        """List PureGym centers grouped by city or area."""
        groups = await service.list_centers()
        return [group.model_dump(mode="json") for group in groups]

    @mcp.tool()
    async def search_classes(
        class_ids: list[int] | None = None,
        center_ids: list[int] | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> list[dict]:
        """Search upcoming classes, optionally filtered by class type, center, or date range."""
        classes = await service.search_classes(class_ids, center_ids, from_date, to_date)
        return [gym_class.model_dump(mode="json") for gym_class in classes]

    if not service.is_authenticated:
        return

    @mcp.tool()
    async def list_my_bookings(
        class_ids: list[int] | None = None,
        center_ids: list[int] | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> list[dict]:
        """List your current booked and waitlisted classes from your PureGym account."""
        classes = await service.list_my_bookings(class_ids, center_ids, from_date, to_date)
        return [gym_class.model_dump(mode="json") for gym_class in classes]

    @mcp.tool()
    async def book_class(booking_id: str, activity_id: int, payment_type: str) -> dict:
        """Book a class or join its waitlist using the identifiers returned by search results."""
        result = await service.book_class(booking_id, activity_id, payment_type)
        return result.model_dump(mode="json")

    @mcp.tool()
    async def cancel_booking(participation_id: str) -> dict:
        """Cancel an existing booking or waitlist entry using its participation id."""
        result = await service.cancel_booking(participation_id)
        return result.model_dump(mode="json")

    @mcp.tool()
    async def get_center_live_status(center_id: int) -> dict:
        """Return current occupancy and busy-hours data for a PureGym center."""
        status = await service.get_center_live_status(center_id)
        return status.model_dump(mode="json")

    @mcp.tool()
    async def get_center_open_hours(center_id: int) -> list[dict]:
        """Return opening and staffed hours for a PureGym center."""
        hours = await service.get_center_open_hours(center_id)
        return [entry.model_dump(mode="json") for entry in hours]
