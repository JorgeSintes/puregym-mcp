from __future__ import annotations

from datetime import datetime, timedelta

from pydantic import BaseModel, computed_field

from puregym_mcp.puregym.api_schemas import (
    ApiBookedClass,
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
        center = item.center
        participation = item.participation
        return cls(
            date=item.date,
            start_time=_normalize_time(item.startTime),
            end_time=_normalize_time(item.endTime),
            title=item.name,
            activity_id=item.activity.activityId,
            booking_id=item.bookingId.booking_id,
            payment_type=item.payment_type or "free",
            participation_id=participation.participation_id if participation else None,
            instructor=item.instructorName or "",
            location=item.roomName or "",
            center_id=_coerce_int(center.cid) if center else None,
            center_name=(center.centerName or center.webname or "") if center else "",
            center_url=_build_center_url(center.slug if center else None),
            duration=_duration_minutes(item.startTime, item.endTime),
            activity_url=_build_activity_url(item.activity.slug),
            level=item.activity.level,
            booked_count=item.bookedCount,
            class_capacity=item.classCapacity,
            waitlist_position=item.participationListIndex,
            waitlist_size=item.waitingListCount,
            can_cancel=item.can_cancel,
            state=item.state,
        )

    @classmethod
    def from_api_booking(cls, item: ApiBookedClass) -> "GymClass":
        booking = item.booking
        center = booking.center
        participation = item.participationId
        return cls(
            date=booking.date,
            start_time=_normalize_time(booking.startTime),
            end_time=_normalize_time(booking.endTime),
            title=booking.name,
            activity_id=booking.activity.activityId,
            booking_id=booking.bookingId.booking_id,
            payment_type=item.payment_type or booking.payment_type or "free",
            participation_id=participation.participation_id if participation else None,
            instructor=booking.instructorName or "",
            location=booking.roomName or ((center.centerName or center.webname) if center else "") or "",
            center_id=_coerce_int(center.cid) if center else None,
            center_name=(center.centerName or center.webname or "") if center else "",
            center_url=_build_center_url(center.slug if center else None),
            duration=_duration_minutes(booking.startTime, booking.endTime),
            activity_url=_build_activity_url(booking.activity.slug),
            level=booking.activity.level,
            booked_count=item.bookedCount,
            class_capacity=item.classCapacity,
            waitlist_position=None if item.state == "BOOKED" else item.participationListIndex,
            waitlist_size=item.waitingListCount,
            can_cancel=item.can_cancel,
            state=item.state,
        )

    @classmethod
    def from_web_search_item(cls, item: dict) -> "GymClass":
        button = item.get("button") or {}
        description = button.get("description") if isinstance(button, dict) else None
        return cls(
            date=item["date"],
            start_time=_normalize_time(item["startTime"]),
            end_time=_normalize_time(item["endTime"]),
            title=item["title"],
            activity_id=item["activityId"],
            booking_id=item["bookingId"],
            payment_type=item["payment_type"],
            participation_id=item.get("participationId"),
            instructor=item.get("instructor", ""),
            location=item.get("location", ""),
            center_name=item.get("centerName", item.get("location", "")),
            center_url=item.get("centerUrl", ""),
            duration=item["duration"],
            activity_url=item.get("activityUrl", ""),
            level=_extract_level(item.get("level")),
            waitlist_position=_parse_waitlist_position(description),
            waitlist_size=_parse_waitlist_size(description),
            state="BOOKED" if item.get("participationId") else None,
        )

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
        return cls.model_validate(item.model_dump())


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
        return cls(
            center_id=_coerce_int(item.cid) or item.id,
            center_name=item.centerName or item.webname or "",
            webname=item.webname or item.centerName or "",
            city=item.city or "",
            address_1=item.adress1 or "",
            address_2=item.adress2 or "",
            zip=item.zip or "",
            phone=item.phone,
            email=item.email,
            geo_lat=float(item.geo_lat or 0.0),
            geo_lng=float(item.geo_lng or 0.0),
            opening_hours=[CenterOpeningHours.from_api(entry) for entry in item.opening_hours],
            people_in_center=item.capacity.people_in_center,
            max_capacity=item.capacity.max_capacity,
            capacity_status=item.capacity.capacity_status,
            chart_data={
                weekday: [CenterCapacityPoint.from_api(point) for point in points]
                for weekday, points in item.capacity.chart_data.items()
            },
        )

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
        return cls.model_validate(item.model_dump())


def _normalize_time(value: str) -> str:
    if len(value) == 5:
        return f"{value}:00"
    return value


def _duration_minutes(start_time: str, end_time: str) -> int:
    start = datetime.strptime(_normalize_time(start_time), "%H:%M:%S")
    end = datetime.strptime(_normalize_time(end_time), "%H:%M:%S")
    if end < start:
        end += timedelta(days=1)
    return int((end - start).total_seconds() // 60)


def _extract_level(value: object) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("value", "label", "name"):
            candidate = value.get(key)
            if isinstance(candidate, str):
                return candidate
    return None


def _parse_waitlist_position(description: str | None) -> int | None:
    if not description:
        return None
    prefix = "du er nr. "
    normalized = description.lower().replace("å", "a")
    if prefix not in normalized:
        return None
    suffix = normalized.split(prefix, 1)[1].split(" ", 1)[0]
    return int(suffix) if suffix.isdigit() else None


def _parse_waitlist_size(description: str | None) -> int | None:
    if not description or "venteliste" not in description.lower():
        return None
    start = description.find("(")
    end = description.find(")", start + 1)
    if start == -1 or end == -1:
        return None
    candidate = description[start + 1 : end]
    return int(candidate) if candidate.isdigit() else None


def _build_center_url(slug: str | None) -> str:
    if not slug:
        return ""
    return f"https://www.puregym.dk/find-center/{slug}"


def _build_activity_url(slug: str | None) -> str:
    if not slug:
        return ""
    return f"https://www.puregym.dk/holdtraening/{slug}"


def _coerce_int(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
