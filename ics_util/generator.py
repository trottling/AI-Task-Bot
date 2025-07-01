import datetime
import logging
import tempfile
import uuid
from typing import Iterable, Optional

logger = logging.getLogger(__name__)


def _escape(value: str) -> str:
    """Escape special characters for ICS."""
    return value.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _format_datetime(dt: datetime.datetime) -> str:
    """Return datetime formatted for ICS as UTC."""
    return dt.strftime("%Y%m%dT%H%M%SZ")


def _create_event(task: dict) -> str | None:
    """Build VEVENT string from task dict."""
    title = task.get("title")
    date_str = task.get("date")
    if not title or not date_str:
        return None

    try:
        date_dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        logger.warning("Некорректная дата: %s", date_str)
        return None

    time_str = (task.get("time") or "00:00").strip()
    try:
        hour, minute = map(int, time_str.split(":", 1))
    except ValueError:
        logger.warning("Некорректное время: %s", time_str)
        hour = minute = 0

    start_dt = date_dt.replace(hour=hour, minute=minute)
    end_dt = start_dt + datetime.timedelta(hours=1)

    lines = [
        "BEGIN:VEVENT",
        f"UID:{uuid.uuid4()}",
        f"DTSTAMP:{_format_datetime(datetime.datetime.utcnow())}",
        f"DTSTART:{_format_datetime(start_dt)}",
        f"DTEND:{_format_datetime(end_dt)}",
        f"SUMMARY:{_escape(title)}",
    ]

    description = task.get("description")
    if description:
        lines.append(f"DESCRIPTION:{_escape(description)}")

    location = task.get("location")
    if location:
        lines.append(f"LOCATION:{_escape(location)}")

    lines.append("END:VEVENT")
    return "\r\n".join(lines)


def generate_ics(event_tasks: Iterable[dict]) -> Optional[str]:
    """Create ICS file from tasks and return path to it."""
    events = []
    for task in event_tasks:
        event = _create_event(task)
        if event:
            events.append(event)

    if not events:
        return None

    lines = [
        "BEGIN:VCALENDAR",
        "PRODID:-//Task AI Bot//",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Codex events",
        "X-WR-TIMEZONE:UTC",
    ]
    lines.extend(events)
    lines.append("END:VCALENDAR")
    content = "\r\n".join(lines) + "\r\n"

    try:
        with tempfile.NamedTemporaryFile("w", suffix=".ics", delete=False, encoding="utf-8") as f:
            f.write(content)
            return f.name
    except Exception as e:
        logger.exception("Ошибка генерации ICS: %s", e)
        return None
