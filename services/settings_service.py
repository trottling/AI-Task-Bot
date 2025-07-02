import logging
from storage.sqlite import Database

logger = logging.getLogger(__name__)

class SettingsService:
    def __init__(self, db: Database):
        self.db = db 