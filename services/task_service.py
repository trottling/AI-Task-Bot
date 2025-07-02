import json
import logging
from typing import Any, Optional

from ics.creator import ICSCreator
from loader import openai_service
from storage.sqlite import Database

logger = logging.getLogger(__name__)

class TaskService:
    def __init__(self, db: Database, ics_creator: ICSCreator):
        self.db = db
        self.ics_creator = ics_creator

    async def process_task_text(
        self,
        text: str,
        user_id: int,
    ) -> dict[str, Any]:
        """
        Проверяет текст, вызывает AI, сохраняет запрос, возвращает результат.
        Возвращает dict с ключами: success, message, ai_response, ics_filename (если есть).
        """
        if len(text) < 15:
            return {"success": False, "message": "⛔️ Слишком маленькое сообщение"}
        if len(text) > 750:
            return {"success": False, "message": "⛔️ Слишком большое сообщение"}

        try:
            ai_response = await openai_service.ask(text)
            self.db.add_request(text, user_id, json.dumps(ai_response, ensure_ascii=False))
        except Exception as e:
            logger.exception(f"AI error: {e}")
            return {"success": False, "message": "❌ Не удалось создать список задач:\nНет ответа"}

        if not ai_response:
            return {"success": False, "message": "❌ Не удалось создать список задач:\nПустой ответ"}
        if ai_response.get("error"):
            extra = f" {ai_response['response']}" if ai_response.get('response') else ""
            return {"success": False, "message": f"❌ Не удалось создать список задач:\n{ai_response['error']}{extra}"}
        if "events_tasks" not in ai_response:
            return {"success": False, "message": "❌ Не удалось создать список задач:\nв JSON отсутствует поле 'events_tasks'"}

        event_tasks = [
            t for t in ai_response["events_tasks"]
            if t.get("type", "").strip().lower() in ["event", "task"]
        ]
        if not event_tasks:
            return {"success": True, "message": ai_response.get("response", "")}

        return {
            "success": True,
            "message": ai_response.get("response", ""),
            "ai_response": ai_response,
            "event_tasks": event_tasks,
        }

    def generate_ics(
        self,
        event_tasks: list[dict[str, Any]],
            ) -> Optional[str]:
        # settings = self.db.get_settings(user_id) or {}
        ics_filename = self.ics_creator.create_ics({"events_tasks": event_tasks})
        return ics_filename 