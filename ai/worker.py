import datetime
import json
import logging

from config.config import AI_API_MODEL, AI_USER_PROMPT, AI_SYSTEM_PROMPT, AI_SCHEMA
from loader import ai_client

logger = logging.getLogger(__name__)


async def ask_ai(text: str) -> dict:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prompt = AI_USER_PROMPT.replace("{msg}", text).replace("{time}", now)

    try:
        response = await ai_client.responses.create(
            model=AI_API_MODEL,
            input=prompt,
            instructions=AI_SYSTEM_PROMPT,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "events_tasks_schema",
                    "schema": json.loads(AI_SCHEMA),
                    }
                },
            )

        content = response.output_text.strip()

    except Exception as e:
        logger.warning(f"Ошибка при запросе к AI: {e}")
        return {}

    # Обработка JSON-ответа
    json_start = content.find("{")
    json_end = content.rfind("}")

    if json_start == -1 or json_end == -1:
        logger.exception("JSON not found in AI response")
        return {}

    json_str = content[json_start:json_end + 1]
    json_str.replace("'", '"').strip().encode(encoding="utf-8", errors="ignore")
    clean_resp = json_str.replace("\n", "")
    logger.info(f"AI response: {clean_resp}")

    try:
        return json.loads(json_str)
    except Exception:
        logger.exception("Ошибка парсинга JSON")
        return {}
