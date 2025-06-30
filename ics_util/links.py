import datetime
from typing import Optional, Dict
from urllib.parse import urlencode, quote_plus


def build_links(task: dict) -> Optional[Dict[str, str]]:
    """Create calendar links for Google, Yandex and Mail.ru."""
    title = task.get("title")
    date_str = task.get("date")
    if not title or not date_str:
        return None

    try:
        date_dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None

    time_str = (task.get("time") or "00:00").strip()
    try:
        hour, minute = map(int, time_str.split(":", 1))
    except ValueError:
        hour = minute = 0

    start_dt = date_dt.replace(hour=hour, minute=minute)
    end_dt = start_dt + datetime.timedelta(hours=1)

    start_google = start_dt.strftime("%Y%m%dT%H%M%S")
    end_google = end_dt.strftime("%Y%m%dT%H%M%S")

    params = {
        "action": "TEMPLATE",
        "text": title,
        "dates": f"{start_google}/{end_google}",
        "details": task.get("description", ""),
        "location": task.get("location", ""),
    }
    google_link = (
        "https://calendar.google.com/calendar/render?" + urlencode(params, quote_via=quote_plus)
    )

    start_str = start_dt.strftime("%Y-%m-%dT%H:%M")
    end_str = end_dt.strftime("%Y-%m-%dT%H:%M")

    yandex_params = {
        "name": title,
        "text": task.get("description", ""),
        "location": task.get("location", ""),
        "startDate": start_str,
        "endDate": end_str,
    }
    yandex_link = "https://calendar.yandex.ru/?" + urlencode(yandex_params, quote_via=quote_plus)

    mailru_params = {
        "name": title,
        "text": task.get("description", ""),
        "location": task.get("location", ""),
        "start": start_str,
        "end": end_str,
    }
    mailru_link = "https://calendar.mail.ru/?" + urlencode(mailru_params, quote_via=quote_plus)

    return {"google": google_link, "yandex": yandex_link, "mailru": mailru_link}

