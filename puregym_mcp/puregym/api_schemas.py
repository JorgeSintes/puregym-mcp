from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


class ApiSchema(BaseModel):
    model_config = ConfigDict(extra="allow")


class ApiActivityGroup(ApiSchema):
    bookableViaAPI: bool | None = None
    id: int
    name: str


class ApiActivity(ApiSchema):
    activityId: int
    name: str
    slug: str | None = None
    level: str | None = None
    group: ApiActivityGroup | None = None
    description: str | None = None
    image_url: str | None = None
    image_small: str | None = None
    subgroup_name: str | None = None
    seatBooking: str | None = None


class ApiBookingKey(ApiSchema):
    center: int | None = None
    id: int | None = None
    booking_id: str


class ApiParticipationKey(ApiSchema):
    center: int | None = None
    id: int | None = None
    participation_id: str


class ApiInstructorName(ApiSchema):
    first: str | None = None
    last: str | None = None
    full: str | None = None


class ApiInstructorPersonKey(ApiSchema):
    center: int | None = None
    id: int | None = None
    externalId: str | None = None


class ApiInstructor(ApiSchema):
    name: ApiInstructorName | None = None
    personKey: ApiInstructorPersonKey | None = None


class ApiInstructors(ApiSchema):
    instructor: ApiInstructor | None = None


class ApiOpeningHoursEntry(ApiSchema):
    id: int | None = None
    center_id: int | None = None
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
    phone_text: str | None = None
    concrete_date: str | None = None
    concrete_weekday: str | None = None
    staffed: list[dict[str, Any]] | None = None


class ApiCenterSummary(ApiSchema):
    id: int | None = None
    cid: str | int | None = None
    slug: str | None = None
    shortname: str | None = None
    webname: str | None = None
    centerName: str | None = None
    adress1: str | None = None
    adress2: str | None = None
    city: str | None = None
    zip: str | None = None
    country: str | None = None
    email: str | None = None
    phone: str | None = None
    facebookurl: str | None = None
    geo_lat: str | float | None = None
    geo_lng: str | float | None = None
    opening_hours: list[ApiOpeningHoursEntry] | None = None


class ApiSearchClass(ApiSchema):
    activity: ApiActivity
    bookedCount: int | None = None
    bookingId: ApiBookingKey
    classCapacity: int | None = None
    date: str
    description: str | None = None
    endTime: str
    instructorName: str | None = None
    instructorNames: list[str] | None = None
    instructors: ApiInstructors | None = None
    name: str
    roomName: str | None = None
    roomNames: str | None = None
    startTime: str
    waitingListCount: int | None = None
    can_cancel: bool | None = None
    payment_type: str | None = None
    payment_price: int | float | None = None
    is_squash: bool | None = None
    is_beautyangel: bool | None = None
    is_event: bool | None = None
    dateStartTime: str | None = None
    dateEndTime: str | None = None
    center: ApiCenterSummary | None = None
    participation: ApiParticipationKey | None = None
    state: str | None = None
    participationListIndex: int | None = None

    @field_validator("participation", mode="before")
    @classmethod
    def _normalize_participation(cls, v: Any) -> Any:
        if isinstance(v, str):
            return ApiParticipationKey(participation_id=v)
        return v


class ApiBookedClass(ApiSchema):
    booking: ApiSearchClass
    participationId: ApiParticipationKey | None = None
    participationListIndex: int | None = None
    state: str | None = None
    bookedCount: int | None = None
    classCapacity: int | None = None
    waitingListCount: int | None = None
    can_cancel: bool | None = None
    payment_type: str | None = None


class ApiCenterCapacityPoint(ApiSchema):
    hour: int
    people_in_center: int


class ApiCenterCapacity(ApiSchema):
    people_in_center: int
    max_capacity: int
    capacity_status: str
    chart_data: dict[str, list[ApiCenterCapacityPoint]]


class ApiCenterStats(ApiSchema):
    id: int | None = None
    cid: str | int | None = None
    slug: str | None = None
    webname: str | None = None
    centerName: str | None = None
    adress1: str | None = None
    adress2: str | None = None
    city: str | None = None
    zip: str | None = None
    country: str | None = None
    email: str | None = None
    phone: str | None = None
    geo_lat: str | float | None = None
    geo_lng: str | float | None = None
    opening_hours: list[ApiOpeningHoursEntry]
    capacity: ApiCenterCapacity


class ApiUserMe(ApiSchema):
    id: int | None = None
    center_id: int | None = None
    firstname: str | None = None
    lastname: str | None = None
    email: str | None = None
    phone: str | None = None


class ApiDataEnvelope(ApiSchema):
    data: Any
    status: str


class ApiBookClassResponse(ApiSchema):
    status: str
    participationId: str | None = None


class ApiCancelBookingResponse(ApiSchema):
    status: str
