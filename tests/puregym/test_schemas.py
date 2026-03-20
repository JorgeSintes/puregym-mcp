from datetime import date, time

from puregym_mcp.puregym.schemas import GymClass


def make_gym_class(*, participation_id: str | None, description: str | None = None) -> GymClass:
    button = {}
    if description is not None:
        button["description"] = description
    return GymClass.model_validate(
        {
            "date": date(2026, 3, 23).isoformat(),
            "startTime": time(18, 0).isoformat(),
            "endTime": time(19, 0).isoformat(),
            "title": "Body Pump",
            "activityId": 11,
            "bookingId": "b-1",
            "payment_type": "membership",
            "participationId": participation_id,
            "instructor": "Coach",
            "location": "Main Hall",
            "centerName": "Center 1",
            "centerUrl": "/center",
            "duration": 60,
            "activityUrl": "/activity",
            "level": {},
            "button": button,
        }
    )


def test_gym_class_model_dump_includes_derived_fields():
    gym_class = make_gym_class(participation_id="pid-1", description="Du er nr. 40 på ventelisten")

    dumped = gym_class.model_dump(mode="json")

    assert dumped["is_booked"] is True
    assert dumped["is_waitlisted"] is True
    assert dumped["waitlist_position"] == 40
    assert dumped["waitlist_size"] is None
