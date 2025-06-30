import datetime
import json
import logging

from config.config import AI_API_MODEL, AI_MODE, AI_USER_PROMPT, AI_SYSTEM_PROMPT, AI_SCHEMA
from loader import ai_client

logger = logging.getLogger(__name__)


async def ask_ai(text: str) -> dict:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prompt = AI_USER_PROMPT.replace("{msg}", text).replace("{time}", now)
    content = ""

    logger.info(f"Запрос к AI: модель={AI_API_MODEL}, режим={AI_MODE}, время={now}, текст={text}")

    try:
        match AI_MODE:
            case "chat_completions":
                response = await ai_client.chat.completions.create(
                    model=AI_API_MODEL,
                    messages=[
                        {"role": "system", "content": AI_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    response_format=AI_SCHEMA,
                    stream=False,
                )

                content = response.choices[0].message.content.strip()

            case "completions":
                response = await ai_client.completions.create(
                    model=AI_API_MODEL,
                    prompt=prompt,
                    temperature=0.3,
                    stream=False,
                )

                content = response.choices[0].text.strip()

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
    logger.debug(f"AI response: {json_str}")

    try:
        return json.loads(json_str)
    except Exception:
        logger.exception("Ошибка парсинга JSON")
        return {}
