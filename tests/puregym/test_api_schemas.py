from puregym_mcp.puregym.api_schemas import ApiBookedClass, ApiCenterStats, ApiDataEnvelope, ApiSearchClass


def test_api_search_class_parses_nested_payload():
    item = ApiSearchClass.model_validate(
        {
            "activity": {"activityId": 55, "level": "low", "slug": "pilates", "name": "Pilates"},
            "bookedCount": 18,
            "bookingId": {"booking_id": "123b259574", "center": 123},
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
            "participation": {"participation_id": "123pa1", "center": 123},
            "participationListIndex": 4,
            "state": "WAITLISTED",
        }
    )

    assert item.activity.activityId == 55
    assert item.bookingId.booking_id == "123b259574"
    assert item.center is not None
    assert item.center.slug == "kbh-oe-strandvejen"
    assert item.participation is not None
    assert item.participation.participation_id == "123pa1"
    assert item.participationListIndex == 4


def test_api_booked_class_parses_booking_wrapper():
    item = ApiBookedClass.model_validate(
        {
            "booking": {
                "activity": {"activityId": 55, "level": "low", "slug": "pilates", "name": "Pilates"},
                "bookingId": {"booking_id": "123b259574"},
                "date": "2026-03-29",
                "endTime": "10:30",
                "name": "Pilates",
                "startTime": "09:30",
            },
            "participationId": {"participation_id": "123pa1"},
            "state": "BOOKED",
            "bookedCount": 18,
            "classCapacity": 25,
            "waitingListCount": 2,
        }
    )

    assert item.booking.bookingId.booking_id == "123b259574"
    assert item.participationId is not None
    assert item.participationId.participation_id == "123pa1"
    assert item.state == "BOOKED"


def test_api_center_stats_parses_capacity_and_hours():
    item = ApiCenterStats.model_validate(
        {
            "id": 704,
            "cid": 123,
            "slug": "kbh-oe-aarhusgade",
            "webname": "Kbh Ø., Århusgade",
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
                "max_capacity": 123,
                "capacity_status": "low",
                "chart_data": {"monday": [{"hour": 9, "people_in_center": 45}]},
            },
        }
    )

    assert item.capacity.people_in_center == 12
    assert item.capacity.chart_data["monday"][0].hour == 9
    assert item.opening_hours[0].opening == "05:00"


def test_api_data_envelope_accepts_list_payload():
    envelope = ApiDataEnvelope.model_validate({"data": [{"name": "foo"}], "status": "success"})

    assert envelope.status == "success"
    assert envelope.data[0]["name"] == "foo"
