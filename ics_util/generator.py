import datetime
import logging
import tempfile
import uuid
from typing import Iterable, Optional

from icalendar import Calendar, Event

logger = logging.getLogger(__name__)

def _create_event(task: dict) -> Event | None:
    """Собрать объект ``Event`` из словаря."""
    title = task.get("title")
    date_str = task.get("date")
    if not title or not date_str:
        return None
     
    try:
        date_dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        logger.warning("Некорректная дата: %s", date_str)
        return None

    all_day = bool(task.get("all_day"))
    if all_day:
        start_dt = date_dt.date()
        end_dt = start_dt + datetime.timedelta(days=1)
    else:
        time_str = (task.get("time") or "00:00").strip()
        try:
            hour, minute = map(int, time_str.split(":", 1))
        except ValueError:
            logger.warning("Некорректное время: %s", time_str)
            hour = minute = 0
        start_dt = date_dt.replace(hour=hour, minute=minute)
        end_dt = start_dt + datetime.timedelta(hours=1)

    event = Event()
    event.add("uid", str(uuid.uuid4()))
    event.add("dtstamp", datetime.datetime.utcnow())
    event.add("dtstart", start_dt)
    event.add("dtend", end_dt)
    event.add("summary", title)
    description = task.get("description")
    if description:
        event.add("description", description)
    location = task.get("location")
    if location:
        event.add("location", location)
    return event
def generate_ics(event_tasks: Iterable[dict]) -> Optional[str]:
    """Создать ICS-файл и вернуть путь к нему."""
    cal = Calendar()
    cal.add("prodid", "-//Task AI Bot//")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", "PUBLISH")
    cal.add("X-WR-CALNAME", "Codex events")
    cal.add("X-WR-TIMEZONE", "UTC")

    count = 0
    for task in event_tasks:
        event = _create_event(task)
        if event:
            cal.add_component(event)
            count += 1

    if not count:
        return None
      
    try:
        with tempfile.NamedTemporaryFile("wb", suffix=".ics", delete=False) as f:
            f.write(cal.to_ical())
            return f.name
    except Exception as e:
        logger.exception("Ошибка генерации ICS: %s", e)
        return None
