import asyncio
import time
from datetime import date, datetime, timedelta

import httpx
from bs4 import BeautifulSoup

from puregym_mcp.puregym.schemas import CenterGroup, DashboardBooking, GymClass, GymClassTypesGroup

BASE_URL = "https://www.puregym.dk/"
API_URL = "https://www.puregym.dk/api/"
DASHBOARD_URL = "https://www.puregym.dk/dashboard"


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

    async def _request_text(self, method: str, url: str, require_auth: bool = True, **kwargs) -> str:
        if require_auth:
            await self._ensure_authenticated()
        r = await self.client.request(method, url, **kwargs)
        if r.status_code in (401, 403) or "user_login_form" in r.text:
            async with self._login_lock:
                await self.login()
            r = await self.client.request(method, url, **kwargs)
        r.raise_for_status()
        return r.text

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

    async def get_my_bookings(self) -> list[DashboardBooking]:
        html = await self._request_text(
            "GET",
            DASHBOARD_URL,
            require_auth=True,
            timeout=60,
        )
        return parse_dashboard_bookings(html)

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


def parse_dashboard_datetime(raw_datetime: str, today: date | None = None) -> datetime:
    normalized = " ".join(raw_datetime.split())
    today = today or date.today()

    if normalized.lower().startswith("i dag "):
        return datetime.combine(today, datetime.strptime(normalized[6:], "%H:%M").time())
    if normalized.lower().startswith("i morgen "):
        return datetime.combine(today + timedelta(days=1), datetime.strptime(normalized[9:], "%H:%M").time())
    return datetime.fromisoformat(normalized)


def parse_dashboard_bookings(html: str) -> list[DashboardBooking]:
    soup = BeautifulSoup(html, "html.parser")
    cards: list[DashboardBooking] = []

    for card in soup.select(".card-wrap__card"):
        datetime_node = card.select_one(".card-wrap__card-title h2")
        text_block = card.select_one(".card-wrap__card-text p")
        cancel_link = card.select_one("a.cancelClassLink")
        if datetime_node is None or text_block is None or cancel_link is None:
            continue

        raw_datetime = datetime_node.get_text(" ", strip=True)
        parsed_datetime = parse_dashboard_datetime(raw_datetime)
        bold_nodes = text_block.find_all("b")
        title = bold_nodes[0].get_text(" ", strip=True) if bold_nodes else None
        if not title:
            continue

        lines = [line.strip() for line in text_block.get_text("\n").splitlines() if line.strip()]
        location = lines[1] if len(lines) >= 2 else ""
        button_description = None
        if bold_nodes:
            maybe_description = bold_nodes[-1].get_text(" ", strip=True)
            if maybe_description and maybe_description != title:
                button_description = maybe_description

        participation_id = cancel_link.get("data-pid")
        if not participation_id:
            continue

        cards.append(
            DashboardBooking(
                date=parsed_datetime.date().isoformat(),
                startTime=parsed_datetime.time().strftime("%H:%M:%S"),
                title=title,
                location=location,
                centerName=location,
                participationId=participation_id,
                button_description=button_description,
            )
        )

    return cards
