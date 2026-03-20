import asyncio
import time
from datetime import datetime, timedelta

import httpx
from bs4 import BeautifulSoup

from puregym_mcp.puregym.schemas import CenterGroup, GymClass, GymClassTypesGroup

BASE_URL = "https://www.puregym.dk/"
API_URL = "https://www.puregym.dk/api/"


class PureGymClient:
    def __init__(self, username: str | None = None, password: str | None = None):
        self.username = username
        self.password = password
        self.client = httpx.AsyncClient(follow_redirects=True)
        self._login_lock = asyncio.Lock()
        self._auth_checked_at: float | None = None
        self._auth_check_ttl_seconds = 300

    async def login(self) -> None:
        if not self.has_credentials:
            raise ValueError("PureGym credentials are required for authenticated operations")

        r = await self.client.get(BASE_URL)
        soup = BeautifulSoup(r.text, "html.parser")

        form_build_id_input = soup.find("input", {"name": "form_build_id"})

        if form_build_id_input is None:
            raise ValueError("Could not find form_build_id in the login page")

        form_build_id = form_build_id_input.get("value")

        await self.client.post(
            BASE_URL,
            data={
                "form_build_id": form_build_id,
                "form_id": "user_login_form",
                "name": self.username,
                "pass": self.password,
                "redirect_url": "",
                "op": "Log ind",
            },
            timeout=10,
        )
        self._auth_checked_at = time.monotonic()

    async def _auth_probe(self) -> bool:
        r = await self.client.get(f"{API_URL}get_user_search_params")
        if r.status_code in (401, 403):
            return False
        try:
            data = r.json()
        except ValueError:
            return False
        return data.get("search_days_allowed") == 28

    async def _ensure_authenticated(self) -> None:
        if not self.has_credentials:
            raise ValueError("PureGym credentials are required for authenticated operations")
        if self._auth_checked_at is not None:
            if time.monotonic() - self._auth_checked_at < self._auth_check_ttl_seconds:
                return
        if await self._auth_probe():
            self._auth_checked_at = time.monotonic()
            return
        async with self._login_lock:
            await self.login()

    @property
    def has_credentials(self) -> bool:
        return bool(self.username and self.password)

    @property
    def search_days_allowed(self) -> int:
        return 28 if self.has_credentials else 14

    async def _request_json(self, method: str, url: str, require_auth: bool = True, **kwargs):
        if require_auth:
            await self._ensure_authenticated()
        r = await self.client.request(method, url, **kwargs)
        if r.status_code in (401, 403) or "user_login_form" in r.text:
            async with self._login_lock:
                await self.login()
            r = await self.client.request(method, url, **kwargs)
        r.raise_for_status()
        return r.json()

    async def get_all_class_types(self) -> list[GymClassTypesGroup]:
        data = await self._request_json("GET", f"{API_URL}get_activities", require_auth=False)
        return [GymClassTypesGroup.model_validate(c) for c in data["classes"]]

    async def get_all_centers(self) -> list[CenterGroup]:
        data = await self._request_json("GET", f"{API_URL}get_activities", require_auth=False)
        return [CenterGroup.model_validate(c) for c in data["centers"]]

    async def get_available_classes(
        self,
        class_ids: list[int] | None = None,
        center_ids: list[int] | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> list[GymClass]:
        if from_date is None:
            from_date = datetime.today().strftime("%Y-%m-%d")
        if to_date is None:
            to_date = (datetime.today() + timedelta(days=self.search_days_allowed)).strftime("%Y-%m-%d")

        data = await self._request_json(
            "GET",
            f"{API_URL}search_activities",
            require_auth=self.has_credentials,
            params={
                "classes[]": class_ids or [],
                "centers[]": center_ids or [],
                "from": from_date,
                "to": to_date,
            },
        )

        return [
            GymClass.model_validate({**item, "date": day["date"]}) for day in data for item in day["items"]
        ]

    async def book_class(self, gym_class: GymClass):
        return await self._request_json(
            "POST",
            f"{API_URL}book_activity",
            data={
                "bookingId": gym_class.bookingId,
                "activityId": gym_class.activityId,
                "payment_type": gym_class.payment_type,
            },
        )

    async def book_by_ids(self, booking_id: str, activity_id: int, payment_type: str):
        return await self._request_json(
            "POST",
            f"{API_URL}book_activity",
            data={
                "bookingId": booking_id,
                "activityId": activity_id,
                "payment_type": payment_type,
            },
        )

    async def unbook_class(self, gym_class: GymClass):
        return await self._request_json(
            "POST",
            f"{API_URL}unbook_activity",
            data={
                "participationId": gym_class.participationId,
            },
        )

    async def unbook_participation(self, participation_id: str):
        return await self._request_json(
            "POST",
            f"{API_URL}unbook_activity",
            data={"participationId": participation_id},
        )

    async def aclose(self) -> None:
        await self.client.aclose()
