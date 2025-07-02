import datetime
import logging
import tempfile

logger = logging.getLogger(__name__)


class ICSCreator:
    def __init__(self) -> None:
        self.header = (
            "BEGIN:VCALENDAR\n"
            "VERSION:2.0\n"
            "PRODID:-//ICSCreator//EN\n"
            "CALSCALE:GREGORIAN"
        )
        self.footer = "END:VCALENDAR"

    def create_ics(
        self,
        tasks_dict: dict,
        timezone: str = "UTC",
        colors: dict | None = None,
    ) -> str | None:
        try:
            events = tasks_dict.get("events_tasks", [])
            ics_content = [self.header]
            colors = colors or {}

            for event in events:
                uid = datetime.datetime.now().strftime("%Y%m%dT%H%M%S%f")
                dtstamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")
                date = event.get("date")
                all_day = event.get("all_day", False)
                summary = event.get("title") or ""
                description = event.get("description") or ""
                location = event.get("location") or ""
                importance = int(event.get("importance", 0))
                time = event.get("time")
                dtstart = None

                if all_day:
                    dtstart = f"{date.replace('-', '')}"
                elif date and time:
                    dtstart = f"{date.replace('-', '')}T{time.replace(':', '')}00"
                elif date:
                    dtstart = f"{date.replace('-', '')}T000000"

                # Все задачи и события идут как VEVENT
                if event.get("type") == "task":
                    summary = f"📝 {summary}"
                ics_event = (
                    "BEGIN:VEVENT\n"
                    f"UID:{uid}\n"
                    f"DTSTAMP:{dtstamp}\n"
                    f"SUMMARY:{summary}\n"
                    f"DESCRIPTION:{description}\n"
                )

                if all_day:
                    ics_event += f"DTSTART;VALUE=DATE:{dtstart}\n"
                else:
                    ics_event += f"DTSTART;TZID={timezone}:{dtstart}\n"

                if location:
                    ics_event += f"LOCATION:{location}\n"
                color = colors.get(importance)
                if color is None and importance == 0:
                    color = colors.get(0, "#808080")
                if color:
                    ics_event += f"COLOR:{color}\n"
                ics_event += "END:VEVENT"
                ics_content.append(ics_event)

            ics_content.append(self.footer)

            with tempfile.NamedTemporaryFile(mode='w+', suffix='.ics', encoding="utf-8", errors="ignore", delete=False) as f:
                f.write("\n".join(ics_content))
                f.flush()
                logger.info("ICS файл успешно создан: %s", f.name)
                return f.name

        except Exception as exc:
            logger.error("Ошибка создания ICS файла: %s", exc)
            return None

