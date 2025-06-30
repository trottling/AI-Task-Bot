import datetime
import logging
import uuid
from typing import Optional

from ics import Calendar, Event

logger = logging.getLogger(__name__)


def generate_ics(event_task: dict) -> Optional[str]:
    """
    Generate ICS file from event task data
    Returns path to generated file or None if generation failed
    """
    try:
        calendar = Calendar()
        event = Event()
        event.created = datetime.datetime.utcnow()

        # Required fields
        if not event_task.get("title"):
            return None

        event.name = event_task["title"]
        event.description = event_task.get("description", "")
        event.uid = str(uuid.uuid4())

        # Date handling
        date_str = event_task.get("date")
        if not date_str:
            return None

        time_str = event_task.get("time", "00:00")
        datetime_str = f"{date_str}T{time_str}:00"
        
        try:
            event.begin = datetime.datetime.fromisoformat(datetime_str)
        except ValueError:
            return None

        # Set duration to 1 hour if not specified
        event.duration = datetime.timedelta(hours=1)

        calendar.events.add(event)

        # Save to temporary file
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ics", delete=False, errors="ignore") as f:
            f.write(calendar.serialize())
            return f.name

    except Exception:
        logger.exception("Error generating ICS")
        return None
