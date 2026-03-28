from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, computed_field

from puregym_mcp.puregym.api_schemas import (
    ApiBookClassResponse,
    ApiBookedClass,
    ApiCancelBookingResponse,
    ApiCenterCapacityPoint,
    ApiCenterStats,
    ApiOpeningHoursEntry,
    ApiSearchClass,
)


class GymClassType(BaseModel):
    label: str
    value: int
    type: str


class GymClassTypesGroup(BaseModel):
    title: str
    options: list[GymClassType]

    def format(self) -> str:
        lines = [f"<b>{self.title}</b>"]
        for option in self.options:
            lines.append(f"• {option.label} -> <code>{option.value}</code>")
        return "\n".join(lines)


class Center(BaseModel):
    label: str
    value: int
    type: str


class CenterGroup(BaseModel):
    label: str
    weight: int
    options: list[Center]

    def format(self) -> str:
        lines = [f"<b>{self.label}</b>"]
        for option in self.options:
            lines.append(f"• {option.label} -> <code>{option.value}</code>")
        return "\n".join(lines)


class GymClass(BaseModel):
    date: str
    start_time: str
    end_time: str
    title: str
    activity_id: int
    booking_id: str
    payment_type: str
    participation_id: str | None = None
    instructor: str = ""
    location: str = ""
    center_id: int | None = None
    center_name: str = ""
    center_url: str = ""
    duration: int
    activity_url: str = ""
    level: str | None = None
    booked_count: int | None = None
    class_capacity: int | None = None
    waitlist_position: int | None = None
    waitlist_size: int | None = None
    can_cancel: bool | None = None
    state: str | None = None

    @classmethod
    def from_api_search(cls, item: ApiSearchClass) -> "GymClass":
        from puregym_mcp.puregym.adapters import adapt_gym_class_from_search

        return cls(**adapt_gym_class_from_search(item))

    @classmethod
    def from_api_booking(cls, item: ApiBookedClass) -> "GymClass":
        from puregym_mcp.puregym.adapters import adapt_gym_class_from_booking

        return cls(**adapt_gym_class_from_booking(item))

    @classmethod
    def from_web_search_item(cls, item: dict) -> "GymClass":
        from puregym_mcp.puregym.adapters import adapt_gym_class_from_web_search

        return cls(**adapt_gym_class_from_web_search(item))

    @computed_field
    @property
    def is_waitlisted(self) -> bool:
        return self.waitlist_position is not None or (self.waitlist_size or 0) > 0

    @computed_field
    @property
    def is_booked(self) -> bool:
        return self.state == "BOOKED" or self.participation_id is not None


class CenterOpeningHours(BaseModel):
    name: str
    date: str
    opening: str
    closing: str
    staffed_from: str | None = None
    staffed_until: str | None = None
    staffed_from_2: str | None = None
    staffed_until_2: str | None = None
    phone_from: str | None = None
    phone_until: str | None = None
    concrete_date: str | None = None
    concrete_weekday: str | None = None

    @classmethod
    def from_api(cls, item: ApiOpeningHoursEntry) -> "CenterOpeningHours":
        from puregym_mcp.puregym.adapters import adapt_center_opening_hours

        return cls(**adapt_center_opening_hours(item))


class CenterLiveStatus(BaseModel):
    center_id: int
    center_name: str
    webname: str
    city: str
    address_1: str
    address_2: str
    zip: str
    phone: str | None = None
    email: str | None = None
    geo_lat: float
    geo_lng: float
    opening_hours: list[CenterOpeningHours]
    people_in_center: int
    max_capacity: int
    capacity_status: str
    chart_data: dict[str, list[CenterCapacityPoint]]

    @classmethod
    def from_api(cls, item: ApiCenterStats) -> "CenterLiveStatus":
        from puregym_mcp.puregym.adapters import adapt_center_live_status

        return cls(**adapt_center_live_status(item))

    @computed_field
    @property
    def occupancy_ratio(self) -> float | None:
        if self.max_capacity <= 0:
            return None
        return round(self.people_in_center / self.max_capacity, 4)

    @computed_field
    @property
    def is_open_now(self) -> bool | None:
        current = self._current_opening_hours_entry()
        if current is None:
            return None
        now = datetime.now().time()
        opening = datetime.strptime(current.opening, "%H:%M").time()
        closing = datetime.strptime(current.closing, "%H:%M").time()
        if closing.hour == 0 and closing.minute == 0:
            return now >= opening
        return opening <= now <= closing

    @computed_field
    @property
    def staffed_now(self) -> bool | None:
        current = self._current_opening_hours_entry()
        if current is None:
            return None
        now = datetime.now().time()
        staffed_ranges = [
            (current.staffed_from, current.staffed_until),
            (current.staffed_from_2, current.staffed_until_2),
        ]
        for start, end in staffed_ranges:
            if not start or not end:
                continue
            start_time = datetime.strptime(start, "%H:%M").time()
            end_time = datetime.strptime(end, "%H:%M").time()
            if start_time <= now <= end_time:
                return True
        return False

    def _current_opening_hours_entry(self) -> CenterOpeningHours | None:
        weekday = datetime.now().strftime("%A").lower()
        for entry in self.opening_hours:
            if entry.date.lower() == weekday:
                return entry
        return None


class CenterCapacityPoint(BaseModel):
    hour: int
    people_in_center: int

    @classmethod
    def from_api(cls, item: ApiCenterCapacityPoint) -> "CenterCapacityPoint":
        from puregym_mcp.puregym.adapters import adapt_center_capacity_point

        return cls(**adapt_center_capacity_point(item))


class BookClassResult(BaseModel):
    status: str
    participation_id: str | None = None

    @classmethod
    def from_api(cls, item: ApiBookClassResponse) -> "BookClassResult":
        return cls(
            status=item.status,
            participation_id=item.participationId,
        )


class CancelBookingResult(BaseModel):
    status: str

    @classmethod
    def from_api(cls, item: ApiCancelBookingResponse) -> "CancelBookingResult":
        return cls(status=item.status)
