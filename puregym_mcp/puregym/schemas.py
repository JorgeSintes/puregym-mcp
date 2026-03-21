import re

from pydantic import BaseModel, computed_field

WAITLIST_POSITION_PATTERN = re.compile(r"nr\.\s*(\d+)\s+pa\s+ventelisten", re.IGNORECASE)
WAITLIST_SIZE_PATTERN = re.compile(r"Venteliste\s*\((\d+)\)", re.IGNORECASE)


def parse_waitlist_position(description: str | None) -> int | None:
    if description is None:
        return None

    normalized = description.lower().replace("å", "a")
    match = WAITLIST_POSITION_PATTERN.search(normalized)
    if match is None:
        return None
    return int(match.group(1))


def parse_waitlist_size(description: str | None) -> int | None:
    if description is None:
        return None

    match = WAITLIST_SIZE_PATTERN.search(description)
    if match is None:
        return None
    return int(match.group(1))


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
            lines.append(f"• {option.label} → <code>{option.value}</code>")

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
            lines.append(f"• {option.label} → <code>{option.value}</code>")

        return "\n".join(lines)


class GymClass(BaseModel):
    date: str
    startTime: str
    endTime: str
    title: str
    activityId: int
    bookingId: str
    payment_type: str
    participationId: str | None
    instructor: str
    location: str
    centerName: str
    centerUrl: str
    duration: int
    activityUrl: str
    level: dict
    button: dict

    @computed_field
    @property
    def button_description(self) -> str | None:
        description = self.button.get("description")
        if isinstance(description, str):
            return description
        return None

    @computed_field
    @property
    def waitlist_position(self) -> int | None:
        return parse_waitlist_position(self.button_description)

    @computed_field
    @property
    def waitlist_size(self) -> int | None:
        return parse_waitlist_size(self.button_description)

    @computed_field
    @property
    def is_waitlisted(self) -> bool:
        return self.waitlist_position is not None or self.waitlist_size is not None

    @computed_field
    @property
    def is_booked(self) -> bool:
        return self.participationId is not None


class DashboardBooking(BaseModel):
    date: str
    startTime: str
    title: str
    location: str
    centerName: str
    participationId: str
    button_description: str | None = None

    @computed_field
    @property
    def waitlist_position(self) -> int | None:
        return parse_waitlist_position(self.button_description)

    @computed_field
    @property
    def waitlist_size(self) -> int | None:
        return parse_waitlist_size(self.button_description)

    @computed_field
    @property
    def is_waitlisted(self) -> bool:
        return self.waitlist_position is not None or self.waitlist_size is not None

    @computed_field
    @property
    def is_booked(self) -> bool:
        return True
