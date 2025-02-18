import datetime
import random

from ics import Calendar, Event


def generate_ics(event_task):
    calendar = Calendar()

    event = Event()
    event.name = event_task.get("title", "Без названия")
    event.description = event_task.get("description", "")

    date_str = event_task.get("date")
    time_str = event_task.get("time")

    if date_str:
        if time_str:
            datetime_str = f"{date_str}T{time_str}:00"
        else:
            datetime_str = f"{date_str}T00:00:00"
        event.begin = datetime.datetime.fromisoformat(datetime_str)

    calendar.events.add(event)

    return calendar
