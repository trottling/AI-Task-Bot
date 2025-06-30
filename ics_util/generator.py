"""Утилиты для генерации ICS-файлов."""

import datetime
import logging
import tempfile
import uuid
from typing import Iterable, Optional

logger = logging.getLogger(__name__)

def _fmt(dt: datetime.datetime) -> str:
    """Вернуть строку даты для ICS."""
    return dt.strftime("%Y%m%dT%H%M%S")


def _event_to_lines(event: dict) -> list[str]:
    """Преобразовать словарь события в строки ICS."""
    title = event.get("title")
    date_str = event.get("date")
    if not title or not date_str:
        return []

    time_str = event.get("time") or "00:00"

    try:
        date_dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        logger.warning("Некорректная дата: %s", date_str)
        return []

    try:
        hour, minute = map(int, time_str.split(":", 1))
    except ValueError:
        logger.warning("Некорректное время: %s", time_str)
        hour = minute = 0

    start = date_dt.replace(hour=hour, minute=minute)
    end = start + datetime.timedelta(hours=1)

    lines = [
        "BEGIN:VEVENT",
        f"UID:{uuid.uuid4()}",
        f"DTSTAMP:{_fmt(datetime.datetime.utcnow())}Z",
        f"DTSTART:{_fmt(start)}",
        f"DTEND:{_fmt(end)}",
        f"SUMMARY:{title}",
    ]

    description = event.get("description", "")
    if description:
        lines.append(f"DESCRIPTION:{description}")

    location = event.get("location")
    if location:
        lines.append(f"LOCATION:{location}")

    lines.append("END:VEVENT")
    return lines


def generate_ics(event_tasks: Iterable[dict]) -> Optional[str]:
    """Создать ICS-файл из переданных событий."""
    events: list[str] = []
    for task in event_tasks:
        events.extend(_event_to_lines(task))

    if not events:
        return None

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "PRODID:-//Task AI Bot//EN",
        "X-WR-CALNAME:Codex events",
        "X-WR-TIMEZONE:UTC",
    ] + events + ["END:VCALENDAR"]

    try:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".ics", delete=False, encoding="utf-8"
        ) as f:
            f.write("\n".join(lines))
            return f.name
    except Exception as e:
        logger.exception("Ошибка генерации ICS: %s", e)
        return None
