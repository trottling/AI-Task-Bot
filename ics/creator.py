import datetime
import logging
import tempfile
from typing import Any, Optional

from geopy.geocoders import Nominatim

logger = logging.getLogger(__name__)


class ICSCreator:
    def __init__(self) -> None:
        self.header: str = (
            "BEGIN:VCALENDAR\n"
            "VERSION:2.0\n"
            "PRODID:-//ICSCreator//EN\n"
            "CALSCALE:GREGORIAN"
        )
        self.footer: str = "END:VCALENDAR"
        self.geolocator = Nominatim(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")

    def create_ics(self, tasks: dict[str, Any], ) -> Optional[str]:
        """
        Генерирует ICS-файл из списка задач/событий.
        Возвращает путь к временному файлу или None при ошибке.
        """
        try:
            events = tasks.get("events_tasks", [])
            ics_content: list[str] = [self.header]

            for event in events:
                uid = datetime.datetime.now().strftime("%Y%m%dT%H%M%S%f")
                date_stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")
                date = event.get("date")
                all_day = event.get("all_day", False)
                summary = event.get("title") or ""
                description = event.get("description") or ""
                location = event.get("location") or ""
                importance = int(event.get("importance", 0))
                geo = event.get("geo")
                time = event.get("time")
                date_start = None

                if all_day:
                    date_start = f"{date.replace('-', '')}"
                elif date and time:
                    date_start = f"{date.replace('-', '')}T{time.replace(':', '')}00"
                elif date:
                    date_start = f"{date.replace('-', '')}T000000"

                # Все задачи и события идут как VEVENT
                if event.get("type") == "task":
                    summary = f"📝 {summary}"

                ics_event = (
                    "BEGIN:VEVENT\n"
                    f"UID:{uid}\n"
                    f"DTSTAMP:{date_stamp}\n"
                    f"SUMMARY:{summary}\n"
                    f"DESCRIPTION:{description}\n"
                )

                if all_day:
                    ics_event += f"DTSTART;VALUE=DATE:{date_start}\n"
                else:
                    ics_event += f"DTSTART;TZID=UTC:{date_start}\n"

                # Локация или линк на созвон
                if location:
                    ics_event += f"LOCATION:{location}\n"

                # Координаты
                if geo:
                    try:
                        geotag = self.geolocator.geocode(geo)
                        if geotag and geotag.latitude and geotag.longitude:
                            ics_event += f"GEO:{geotag.latitude};{geotag.longitude}\n"
                    except Exception as e:
                        logger.error(f"Ошибка получения координат локации: {e}")

                # Квадрат эйзенхауэра и цвет таски
                match importance:
                    case 1:
                        color = "#E84E4E"  # Красный - Важно - Срочно
                    case 2:
                        color = "#2A96F9"  # Синий - Важно - Не срочно
                    case 3:
                        color = "#DDAD33"  # Желтый - Не важно - Срочно
                    case 4:
                        color = "#73C160"  # Зеленый - Не важно - Не срочно
                    case 0:
                        color = "#878787"  # Серый
                    case _:
                        color = "#878787"  # Серый

                if color != "":
                    ics_event += f"COLOR:{color}\n"

                ics_event += "END:VEVENT"
                ics_content.append(ics_event)

            ics_content.append(self.footer)

            with tempfile.NamedTemporaryFile(mode='w+', suffix='.ics', encoding="utf-8", errors="ignore", delete=False) as f:
                f.write("\n".join(ics_content))
                f.flush()
                logger.info(f"ICS файл успешно создан: {f.name}")
                return f.name

        except Exception as e:
            logger.error(f"Ошибка создания ICS файла: {e}", )
            return None
