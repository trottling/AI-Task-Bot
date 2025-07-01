import logging
import sqlite3
from datetime import datetime


logger = logging.getLogger(__name__)


class Database:
    """Lightweight SQLite helper."""

    def __init__(self, path_to_db: str) -> None:
        self.path_to_db = path_to_db
        self._init_db()

    def _init_db(self) -> None:
        create_users = """
        CREATE TABLE IF NOT EXISTS Users (
            telegram_id INTEGER PRIMARY KEY,
            full_name TEXT,
            is_allowed INTEGER DEFAULT 0
        );
        """
        create_requests = """
        CREATE TABLE IF NOT EXISTS REQUESTS (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            req_time TEXT,
            req_text TEXT,
            req_user_id INTEGER,
            req_resp TEXT
        );
        """
        with sqlite3.connect(self.path_to_db) as connection:
            cursor = connection.cursor()
            cursor.execute(create_users)
            cursor.execute(create_requests)
            connection.commit()

    def execute(
        self,
        sql: str,
        parameters: tuple | None = None,
        *,
        fetchone: bool = False,
        fetchall: bool = False,
        commit: bool = False,
    ):
        parameters = parameters or ()
        data = None
        with sqlite3.connect(self.path_to_db) as connection:
            connection.set_trace_callback(logger.debug)
            cursor = connection.cursor()
            cursor.execute(sql, parameters)

            if commit:
                connection.commit()
            if fetchone:
                data = cursor.fetchone()
            if fetchall:
                data = cursor.fetchall()

        return data

    def add_user(self, telegram_id: int, full_name: str, allowed: bool = False) -> None:
        if self.user_exists(telegram_id):
            logger.info("Пользователь %s уже существует", telegram_id)
            return
        sql = "INSERT INTO Users(telegram_id, full_name, is_allowed) VALUES(?, ?, ?);"
        self.execute(sql, (telegram_id, full_name, int(allowed)), commit=True)

    def user_exists(self, telegram_id: int) -> bool:
        sql = "SELECT 1 FROM Users WHERE telegram_id = ? LIMIT 1;"
        return self.execute(sql, (telegram_id,), fetchone=True) is not None

    def has_access(self, telegram_id: int) -> bool:
        sql = "SELECT is_allowed FROM Users WHERE telegram_id = ? LIMIT 1;"
        row = self.execute(sql, (telegram_id,), fetchone=True)
        return bool(row and row[0])

    def set_access(self, telegram_id: int, allowed: bool) -> None:
        if self.user_exists(telegram_id):
            sql = "UPDATE Users SET is_allowed = ? WHERE telegram_id = ?;"
            self.execute(sql, (int(allowed), telegram_id), commit=True)
        else:
            self.add_user(telegram_id, "", allowed)

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM Users;", fetchone=True)

    def count_reqs(self):
        return self.execute("SELECT COUNT(*) FROM REQUESTS;", fetchone=True)

    def add_request(self, req_text: str, req_user_id: int, req_resp: str) -> None:
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = (
                "INSERT INTO REQUESTS(req_time, req_text, req_user_id, req_resp) "
                "VALUES(?, ?, ?, ?);"
            )
            self.execute(sql, (now, req_text, req_user_id, req_resp), commit=True)
        except Exception as exc:
            logger.exception("Не удалось сохранить запрос: %s", exc)

