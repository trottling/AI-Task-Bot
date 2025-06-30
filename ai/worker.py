import datetime
import json
import logging

from ai.prompt import PROMPT
from config.config import AI_API_MODEL
from loader import ai_client

logger = logging.getLogger(__name__)


async def ask_ai(text: str) -> dict:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prompt = PROMPT.replace("{msg}", text).replace("{time}", now)

    response = await ai_client.completions.create(
        model=AI_API_MODEL,
        prompt=prompt,
        temperature=1.3,
        stream=False,
    )

    try:
        content = response.choices[0].text.strip()
    except Exception:
        logger.exception("Unexpected AI response format")
        return {}

    json_start = content.find("{")
    json_end = content.rfind("}")
    if json_start == -1 or json_end == -1:
        logger.exception("JSON not found in AI response")
        return {}

    json_str = content[json_start:json_end + 1]
    print(json_str)
    try:
        return json.loads(json_str)
    except Exception:
        logger.exception("JSON parsing failed for AI response")
        return { }
