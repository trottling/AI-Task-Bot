import datetime
import logging

from ai_utils.prompt import PROMPT
from data.config import AI_API_MODEL
from loader import ai_client

logger = logging.getLogger(__name__)


async def ask_ai(text: str) -> str:
    text = f"{text}\n\nТекущая дата: {datetime.date.today()}"

    response = await ai_client.chat.completions.create(
        model=AI_API_MODEL,
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=1.3,
        stream=False,
    )

    try:
        return response["message"]["content"]
    except Exception:
        logger.exception("Unexpected AI response format")
        return ""
