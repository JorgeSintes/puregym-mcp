from datetime import datetime, time
from typing import Protocol

from puregym_mcp.puregym.models import GymClass


class TimeSlotLike(Protocol):
    day_of_week: int
    start_time: time
    end_time: time


def filter_by_booked(classes: list[GymClass], booked: bool = True) -> list[GymClass]:
    return [c for c in classes if (c.participation_id is not None) == booked]


def filter_by_time_slot(classes: list[GymClass], time_slot: TimeSlotLike) -> list[GymClass]:
    filtered_classes = []
    for c in classes:
        date = datetime.fromisoformat(c.date)
        if date.weekday() != time_slot.day_of_week:
            continue

        class_start = time.fromisoformat(c.start_time)
        class_end = time.fromisoformat(c.end_time)
        if time_slot.start_time <= class_start <= class_end <= time_slot.end_time:
            filtered_classes.append(c)
    return filtered_classes


def filter_by_time_slots(classes: list[GymClass], time_slots: list[TimeSlotLike]) -> list[GymClass]:
    filtered_classes = []

    for time_slot in time_slots:
        filtered_classes.extend(filter_by_time_slot(classes, time_slot))

    return filtered_classes
