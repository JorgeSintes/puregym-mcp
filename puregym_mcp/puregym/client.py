from __future__ import annotations

import base64
from datetime import datetime, timedelta
from typing import Any

import httpx

from puregym_mcp.puregym.api_schemas import (
    ApiBookClassResponse,
    ApiBookedClass,
    ApiCancelBookingResponse,
    ApiCenterStats,
    ApiDataEnvelope,
    ApiSearchClass,
)
from puregym_mcp.puregym.models import (
    BookClassResult,
    CancelBookingResult,
    CenterGroup,
    CenterLiveStatus,
    CenterOpeningHours,
    GymClass,
    GymClassTypesGroup,
)

BASE_URL = "https://www.puregym.dk/"
WEB_API_URL = "https://www.puregym.dk/api/"
APP_BASE_URL = "https://mit.puregym.dk/"
APP_API_URL = f"{APP_BASE_URL}api/v1.0.0"
APP_IDENTIFIER = "com.shapehq.fitnessworld.android"
APP_GDPR = "android"
APP_USER_AGENT = "okhttp/5.1.0"


class PureGymClient:
    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        timeout: float | None = None,
    ):
        self.username = username
        self.password = password
        self.client = httpx.AsyncClient(follow_redirects=True, timeout=timeout)

    @property
    def has_credentials(self) -> bool:
        return bool(self.username and self.password)

    @property
    def search_days_allowed(self) -> int:
        return 28 if self.has_credentials else 14

    def _app_headers(self, *, content_type: str | None = None) -> dict[str, str]:
        if not self.has_credentials:
            raise ValueError("PureGym credentials are required for authenticated operations")
        token = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        headers = {
            "authorization": f"Basic {token}",
            "app-identifier": APP_IDENTIFIER,
            "gdpr": APP_GDPR,
            "user-agent": APP_USER_AGENT,
        }
        if content_type is not None:
            headers["content-type"] = content_type
        return headers

    async def _request_web_json(self, method: str, url: str, **kwargs: Any) -> Any:
        response = await self.client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    async def _request_app_json(self, method: str, path: str, **kwargs: Any) -> Any:
        headers = self._app_headers(content_type=kwargs.pop("content_type", None))
        extra_headers = kwargs.pop("headers", None)
        if extra_headers:
            headers.update(extra_headers)
        response = await self.client.request(method, f"{APP_API_URL}{path}", headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()

    async def get_all_class_types(self) -> list[GymClassTypesGroup]:
        data = await self._request_web_json("GET", f"{WEB_API_URL}get_activities")
        return [GymClassTypesGroup.model_validate(group) for group in data["classes"]]

    async def get_all_centers(self) -> list[CenterGroup]:
        data = await self._request_web_json("GET", f"{WEB_API_URL}get_activities")
        return [CenterGroup.model_validate(group) for group in data["centers"]]

    async def get_available_classes(
        self,
        class_ids: list[int] | None = None,
        center_ids: list[int] | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> list[GymClass]:
        if self.has_credentials:
            payload = {
                "activities": class_ids or [],
                "centers": center_ids or [],
                "endTime": "23:59",
                "id": 0,
                "instructor": "",
                "startTime": "00:00",
                "title": "",
                "weekdays": [0, 1, 2, 3, 4, 5, 6],
            }
            raw_data = await self._request_app_json(
                "POST",
                "/bookings/search",
                content_type="application/json; charset=UTF-8",
                json=payload,
            )
            envelope = ApiDataEnvelope.model_validate(raw_data)
            classes = [
                GymClass.from_api_search(ApiSearchClass.model_validate(item)) for item in envelope.data
            ]
            return self._filter_classes_by_date(classes, from_date, to_date)

        from_date = datetime.today().strftime("%Y-%m-%d") if from_date is None else from_date
        to_date = (
            (datetime.today() + timedelta(days=self.search_days_allowed)).strftime("%Y-%m-%d")
            if to_date is None
            else to_date
        )
        data = await self._request_web_json(
            "GET",
            f"{WEB_API_URL}search_activities",
            params={
                "classes[]": class_ids or [],
                "centers[]": center_ids or [],
                "from": from_date,
                "to": to_date,
            },
        )
        classes = [
            GymClass.from_web_search_item({**item, "date": day["date"]})
            for day in data
            for item in day["items"]
        ]

        return classes

    async def get_my_bookings(self) -> list[GymClass]:
        if not self.has_credentials:
            raise ValueError("PureGym credentials are required for authenticated operations")
        raw_data = await self._request_app_json("GET", "/bookings")
        envelope = ApiDataEnvelope.model_validate(raw_data)
        return [GymClass.from_api_booking(ApiBookedClass.model_validate(item)) for item in envelope.data]

    async def get_center_details(self, center_id: int) -> dict[str, Any]:
        data = await self._request_app_json("GET", "/centers")
        for center in data["data"]["list"]:
            if int(center.get("cid", center.get("id"))) == center_id:
                return center
        raise ValueError(f"Center {center_id} not found")

    async def get_center_live_status(self, center_id: int) -> CenterLiveStatus:
        raw_data = await self._request_app_json("GET", f"/centers/stats/{center_id}")
        envelope = ApiDataEnvelope.model_validate(raw_data)
        return CenterLiveStatus.from_api(ApiCenterStats.model_validate(envelope.data["list"]))

    async def get_center_open_hours(self, center_id: int) -> list[CenterOpeningHours]:
        return (await self.get_center_live_status(center_id)).opening_hours

    async def book_by_ids(self, booking_id: str, activity_id: int, payment_type: str) -> BookClassResult:
        raw_data = await self._request_app_json(
            "POST",
            "/bookings/book",
            content_type="application/x-www-form-urlencoded",
            data={"bookingId": booking_id, "activityId": activity_id},
        )
        api_response = ApiBookClassResponse.model_validate(raw_data)
        return BookClassResult.from_api(api_response)

    async def unbook_participation(self, participation_id: str) -> CancelBookingResult:
        raw_data = await self._request_app_json(
            "POST",
            "/bookings/cancelBook",
            content_type="application/x-www-form-urlencoded",
            data={"participationId": participation_id},
        )
        api_response = ApiCancelBookingResponse.model_validate(raw_data)
        return CancelBookingResult.from_api(api_response)

    async def aclose(self) -> None:
        await self.client.aclose()

    def _filter_classes_by_date(
        self, classes: list[GymClass], from_date: str | None, to_date: str | None
    ) -> list[GymClass]:
        filtered = classes
        if from_date is not None:
            filtered = [gym_class for gym_class in filtered if gym_class.date >= from_date]
        if to_date is not None:
            filtered = [gym_class for gym_class in filtered if gym_class.date <= to_date]
        return filtered
