import datetime
import json
import logging
from typing import Any

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(
            self,
            api_client: AsyncOpenAI,
            model: str,
            schema: str,
            system_prompt: str,
            user_prompt: str,
            ) -> None:
        self.api_client = api_client
        self.model = model
        self.schema = schema
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt

    async def ask(self, text: str) -> dict[str, Any]:
        """
        Отправляет текст в OpenAI и возвращает структурированный ответ.
        Возвращает пустой dict при ошибке или некорректном ответе.
        """
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prompt = self.user_prompt.replace("{msg}", text).replace("{time}", now)
        try:
            response = await self.api_client.responses.create(
                model=self.model,
                input=prompt,
                instructions=self.system_prompt,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "events_tasks_schema",
                        "schema": json.loads(self.schema),
                        }
                    },
                )
            content: str = response.output_text.strip()
        except Exception as exc:
            logger.warning("Ошибка при запросе к AI: %s", exc)
            return { }

        json_start = content.find("{")
        json_end = content.rfind("}")
        if json_start == -1 or json_end == -1:
            logger.error("Не найден JSON в ответе AI")
            return { }

        json_str: str = content[json_start:json_end + 1]
        json_str = json_str.replace("'", '"').strip()

        logger.info(f"Ответ AI: {json_str.replace("\n", "")}")

        try:
            return json.loads(json_str)
        except Exception as e:
            logger.exception(f"Ошибка парсинга JSON: {e}")
            return { }
