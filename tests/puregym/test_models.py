from puregym_mcp.puregym.api_schemas import ApiBookedClass, ApiCenterStats, ApiSearchClass
from puregym_mcp.puregym.models import CenterLiveStatus, GymClass


def test_gym_class_from_api_search_flattens_nested_fields():
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
            "participation": {"participation_id": "123pa1"},
            "participationListIndex": 4,
            "state": "WAITLISTED",
        }
    )

    gym_class = GymClass.from_api_search(item)

    assert gym_class.activity_id == 55
    assert gym_class.booking_id == "123b259574"
    assert gym_class.center_id == 123
    assert gym_class.center_name == "Kbh Ø., Strandvejen"
    assert gym_class.participation_id == "123pa1"
    assert gym_class.waitlist_position == 4
    assert gym_class.waitlist_size == 2
    assert gym_class.is_waitlisted is True


def test_gym_class_from_api_booking_keeps_booked_state():
    item = ApiBookedClass.model_validate(
        {
            "booking": {
                "activity": {
                    "activityId": 23742,
                    "level": "low",
                    "slug": "bike-standard",
                    "name": "Bike Standard",
                },
                "bookingId": {"booking_id": "123b257681"},
                "date": "2026-04-08",
                "endTime": "09:55",
                "instructorName": "Coach",
                "name": "Bike Standard",
                "roomName": "Bike",
                "startTime": "09:00",
                "center": {
                    "cid": "123",
                    "centerName": "Kbh Ø., Århusgade",
                    "slug": "kbh-oe-aarhusgade",
                    "id": 704,
                },
            },
            "participationId": {"participation_id": "123pa4685751"},
            "participationListIndex": 13,
            "state": "BOOKED",
            "bookedCount": 17,
            "classCapacity": 33,
            "waitingListCount": 0,
            "can_cancel": True,
            "payment_type": "free",
        }
    )

    gym_class = GymClass.from_api_booking(item)

    assert gym_class.state == "BOOKED"
    assert gym_class.is_booked is True
    assert gym_class.waitlist_position is None
    assert gym_class.can_cancel is True
    assert gym_class.duration == 55


def test_center_live_status_from_api_converts_capacity_and_hours():
    item = ApiCenterStats.model_validate(
        {
            "id": 704,
            "cid": 123,
            "slug": "kbh-oe-aarhusgade",
            "webname": "Kbh Ø., Århusgade",
            "centerName": "Kbh Ø., Århusgade",
            "adress1": "PureGym Århusgade",
            "adress2": "Århusgade 102",
            "city": "København Ø",
            "zip": "2100",
            "geo_lat": "55.7067",
            "geo_lng": "12.5873",
            "opening_hours": [
                {
                    "name": "Mandag",
                    "date": "monday",
                    "opening": "05:00",
                    "closing": "00:00",
                    "staffed_from": "08:00",
                    "staffed_until": "20:00",
                }
            ],
            "capacity": {
                "people_in_center": 12,
                "max_capacity": 120,
                "capacity_status": "low",
                "chart_data": {"monday": [{"hour": 9, "people_in_center": 45}]},
            },
        }
    )

    status = CenterLiveStatus.from_api(item)

    assert status.center_id == 123
    assert status.center_name == "Kbh Ø., Århusgade"
    assert status.people_in_center == 12
    assert status.max_capacity == 120
    assert status.occupancy_ratio == 0.1
    assert status.opening_hours[0].opening == "05:00"
    assert status.chart_data["monday"][0].people_in_center == 45
