import datetime
import json
import logging

from ai_utils.prompt import PROMPT
from ai_utils.schema import JSON_SCHEMA
from config.config import AI_API_MODEL
from loader import ai_client

logger = logging.getLogger(__name__)


async def ask_ai(text: str, user_id: int) -> dict:
    text = f"{text}\n\nТекущая дата: {datetime.date.today()}"

    response = await ai_client.chat.completions.create(
        model=AI_API_MODEL,
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=1.3,
        stream=False,
        user=str(user_id),
        response_format={"type": "json_schema", "json_schema": JSON_SCHEMA},
    )

    try:
        content = response["message"]["content"]
    except Exception:
        logger.exception("Unexpected AI response format")
        return {}

    try:
        return json.loads(content)
    except Exception:
        logger.exception("JSON parsing failed for AI response")
        return {}

