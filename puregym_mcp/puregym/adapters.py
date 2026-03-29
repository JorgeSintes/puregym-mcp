from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from puregym_mcp.puregym.api_schemas import (
        ApiBookedClass,
        ApiCenterCapacityPoint,
        ApiCenterStats,
        ApiOpeningHoursEntry,
        ApiSearchClass,
    )


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


def adapt_gym_class_from_search(item: ApiSearchClass) -> dict:
    """Adapt ApiSearchClass to GymClass constructor kwargs."""
    center = item.center
    participation = item.participation
    return {
        "date": item.date,
        "start_time": _normalize_time(item.startTime),
        "end_time": _normalize_time(item.endTime),
        "title": item.name,
        "activity_id": item.activity.activityId,
        "booking_id": item.bookingId.booking_id,
        "payment_type": item.payment_type or "free",
        "participation_id": participation.participation_id if participation else None,
        "instructor": item.instructorName or "",
        "location": item.roomName or "",
        "center_id": _coerce_int(center.cid) if center else None,
        "center_name": (center.centerName or center.webname or "") if center else "",
        "center_url": _build_center_url(center.slug if center else None),
        "duration": _duration_minutes(item.startTime, item.endTime),
        "activity_url": _build_activity_url(item.activity.slug),
        "level": item.activity.level,
        "booked_count": item.bookedCount,
        "class_capacity": item.classCapacity,
        "waitlist_position": item.participationListIndex,
        "waitlist_size": item.waitingListCount,
        "can_cancel": item.can_cancel,
        "state": item.state,
    }


def adapt_gym_class_from_booking(item: ApiBookedClass) -> dict:
    """Adapt ApiBookedClass to GymClass constructor kwargs."""
    booking = item.booking
    center = item.center
    participation = item.participationId
    return {
        "date": booking.date,
        "start_time": _normalize_time(booking.startTime),
        "end_time": _normalize_time(booking.endTime),
        "title": booking.name,
        "activity_id": booking.activity.activityId,
        "booking_id": booking.bookingId.booking_id,
        "payment_type": item.payment_type or booking.payment_type or "free",
        "participation_id": participation.participation_id if participation else None,
        "instructor": booking.instructorName or "",
        "location": booking.roomName
        or ((center.centerName or center.webname) if center else "")
        or "",
        "center_id": _coerce_int(center.cid) if center else None,
        "center_name": (center.centerName or center.webname or "") if center else "",
        "center_url": _build_center_url(center.slug if center else None),
        "duration": _duration_minutes(booking.startTime, booking.endTime),
        "activity_url": _build_activity_url(booking.activity.slug),
        "level": booking.activity.level,
        "booked_count": item.bookedCount,
        "class_capacity": item.classCapacity,
        "waitlist_position": None
        if item.state == "BOOKED"
        else item.participationListIndex,
        "waitlist_size": item.waitingListCount,
        "can_cancel": item.can_cancel,
        "state": item.state,
    }


def adapt_gym_class_from_web_search(item: dict) -> dict:
    """Adapt web search dict to GymClass constructor kwargs."""
    button = item.get("button") or {}
    description = button.get("description") if isinstance(button, dict) else None
    return {
        "date": item["date"],
        "start_time": _normalize_time(item["startTime"]),
        "end_time": _normalize_time(item["endTime"]),
        "title": item["title"],
        "activity_id": item["activityId"],
        "booking_id": item["bookingId"],
        "payment_type": item["payment_type"],
        "participation_id": item.get("participationId"),
        "instructor": item.get("instructor", ""),
        "location": item.get("location", ""),
        "center_name": item.get("centerName", item.get("location", "")),
        "center_url": item.get("centerUrl", ""),
        "duration": item["duration"],
        "activity_url": item.get("activityUrl", ""),
        "level": _extract_level(item.get("level")),
        "waitlist_position": _parse_waitlist_position(description),
        "waitlist_size": _parse_waitlist_size(description),
        "state": "BOOKED" if item.get("participationId") else None,
    }


def adapt_center_opening_hours(item: ApiOpeningHoursEntry) -> dict:
    """Adapt ApiOpeningHoursEntry to CenterOpeningHours constructor kwargs."""
    return item.model_dump()


def adapt_center_live_status(item: ApiCenterStats) -> dict:
    """Adapt ApiCenterStats to CenterLiveStatus constructor kwargs."""
    from puregym_mcp.puregym.models import CenterCapacityPoint, CenterOpeningHours

    return {
        "center_id": _coerce_int(item.cid) or item.id,
        "center_name": item.centerName or item.webname or "",
        "webname": item.webname or item.centerName or "",
        "city": item.city or "",
        "address_1": item.adress1 or "",
        "address_2": item.adress2 or "",
        "zip": item.zip or "",
        "phone": item.phone,
        "email": item.email,
        "geo_lat": float(item.geo_lat or 0.0),
        "geo_lng": float(item.geo_lng or 0.0),
        "opening_hours": [
            CenterOpeningHours.from_api(entry) for entry in item.opening_hours
        ],
        "people_in_center": item.capacity.people_in_center,
        "max_capacity": item.capacity.max_capacity,
        "capacity_status": item.capacity.capacity_status,
        "chart_data": {
            weekday: [CenterCapacityPoint.from_api(point) for point in points]
            for weekday, points in item.capacity.chart_data.items()
        },
    }


def adapt_center_capacity_point(item: ApiCenterCapacityPoint) -> dict:
    """Adapt ApiCenterCapacityPoint to CenterCapacityPoint constructor kwargs."""
    return item.model_dump()
