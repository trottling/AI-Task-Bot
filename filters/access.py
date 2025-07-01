from aiogram.filters import BaseFilter
from aiogram.types import Message

from storage.sqlite import Database


class HasAccessFilter(BaseFilter):
    def __init__(self, admins: list[int], db: Database) -> None:
        self.admins = admins
        self.db = db

    async def __call__(self, message: Message) -> bool:
        if message.from_user.id in self.admins:
            return True
        return self.db.has_access(message.from_user.id)
