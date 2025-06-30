import datetime
import logging
import uuid
from typing import Optional, Iterable

from ics import Calendar, Event
from ics.grammar.parse import ContentLine

logger = logging.getLogger(__name__)


def generate_ics(event_tasks: Iterable[dict]) -> Optional[str]:
    """Generate an ICS file containing the provided events.

    Args:
        event_tasks: Iterable of dicts describing events.

    Returns:
        Path to generated file or ``None`` if generation failed or no events
        were created.
    """
    try:
        calendar = Calendar()
        calendar.extra.append(ContentLine(name="CALSCALE", value="GREGORIAN"))

        for event_task in event_tasks:
            if not event_task.get("title"):
                continue

            date_str = event_task.get("date")
            if not date_str:
                continue

            time_str = event_task.get("time", "00:00")
            datetime_str = f"{date_str}T{time_str}:00"

            try:
                start_dt = datetime.datetime.fromisoformat(datetime_str)
            except ValueError:
                continue

            event = Event()
            event.created = datetime.datetime.utcnow()
            event.uid = str(uuid.uuid4())
            event.name = event_task["title"]
            event.description = event_task.get("description", "")
            event.begin = start_dt
            event.end = start_dt + datetime.timedelta(hours=1)

            location = event_task.get("location")
            if location:
                event.location = location

            calendar.events.add(event)

        if not calendar.events:
            return None

        # Save to temporary file
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode="w", suffix=".ics", delete=False, errors="ignore") as f:
            f.write(calendar.serialize())
            return f.name

    except Exception:
        logger.exception("Error generating ICS")
        return None
