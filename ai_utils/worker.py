import datetime
import json
import logging

from ai_utils.prompt import PROMPT
from ai_utils.schema import RESPONSE_FORMAT
from config.config import AI_API_MODEL
from loader import ai_client

logger = logging.getLogger(__name__)


async def ask_ai(text: str) -> dict:
    curr_prompt = PROMPT.format(msg=text, time=datetime.datetime.now())

    response = await ai_client.completions.create(
        model=AI_API_MODEL,
        prompt=curr_prompt,
        temperature=1.3,
        stream=False,
        response_format=RESPONSE_FORMAT
        )

    try:
        content = response.choices[0].message.content
    except Exception:
        logger.exception("Unexpected AI response format")
        return { }

    try:
        return json.loads(content)
    except Exception:
        logger.exception("JSON parsing failed for AI response")
        return { }
