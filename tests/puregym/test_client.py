import pytest

from puregym_mcp.puregym.api_schemas import ApiBookedClass, ApiSearchClass
from puregym_mcp.puregym.client import PureGymClient
from puregym_mcp.puregym.models import GymClass


def test_gym_class_from_web_search_item_parses_waitlist_fields():
    gym_class = GymClass.from_web_search_item(
        {
            "date": "2026-03-29",
            "startTime": "09:30",
            "endTime": "10:30",
            "title": "Pilates",
            "activityId": 55,
            "bookingId": "123b259574",
            "payment_type": "free",
            "participationId": None,
            "instructor": "Instructor",
            "location": "Studio",
            "centerName": "Kbh Ø., Strandvejen",
            "centerUrl": "/center",
            "duration": 60,
            "activityUrl": "/activity",
            "level": {"label": "low"},
            "button": {"description": "Du er nr. 2 pa ventelisten - Venteliste (8)"},
        }
    )

    assert gym_class.waitlist_position == 2
    assert gym_class.waitlist_size == 8
    assert gym_class.level == "low"


def test_gym_class_from_api_search_uses_structured_fields():
    item = ApiSearchClass.model_validate(
        {
            "activity": {"activityId": 55, "level": "low", "slug": "pilates", "name": "Pilates"},
            "bookedCount": 18,
            "bookingId": {"booking_id": "123b259574"},
            "classCapacity": 25,
            "date": "2026-03-29",
            "endTime": "10:30",
            "instructorName": "Instructor",
            "name": "Pilates",
            "roomName": "Studio",
            "startTime": "09:30",
            "waitingListCount": 2,
            "payment_type": "free",
            "center": {
                "cid": "123",
                "centerName": "Kbh Ø., Strandvejen",
                "slug": "kbh-oe-strandvejen",
                "id": 1,
            },
            "participation": None,
        }
    )

    gym_class = GymClass.from_api_search(item)

    assert gym_class.activity_id == 55
    assert gym_class.booking_id == "123b259574"
    assert gym_class.waitlist_size == 2
    assert gym_class.duration == 60
    assert gym_class.level == "low"
    assert gym_class.center_id == 123
    assert gym_class.center_url.endswith("kbh-oe-strandvejen")


def test_gym_class_from_api_booking_uses_booking_wrapper():
    item = ApiBookedClass.model_validate(
        {
            "booking": {
                "activity": {"activityId": 55, "level": "low", "slug": "pilates", "name": "Pilates"},
                "bookingId": {"booking_id": "123b259574"},
                "date": "2026-03-29",
                "endTime": "10:30",
                "instructorName": "Instructor",
                "name": "Pilates",
                "roomName": "Studio",
                "startTime": "09:30",
                "center": {
                    "cid": "123",
                    "centerName": "Kbh Ø., Strandvejen",
                    "slug": "kbh-oe-strandvejen",
                    "id": 1,
                },
            },
            "participationId": {"participation_id": "123pa1"},
            "participationListIndex": 5,
            "state": "BOOKED",
            "bookedCount": 18,
            "classCapacity": 25,
            "waitingListCount": 2,
            "can_cancel": True,
            "payment_type": "free",
        }
    )

    gym_class = GymClass.from_api_booking(item)

    assert gym_class.participation_id == "123pa1"
    assert gym_class.state == "BOOKED"
    assert gym_class.waitlist_position is None
    assert gym_class.can_cancel is True


@pytest.mark.asyncio
async def test_client_aclose_closes_http_client():
    client = PureGymClient()

    await client.aclose()

    assert client.client.is_closed
