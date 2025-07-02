import logging
import sqlite3
from datetime import datetime

logger = logging.getLogger(__name__)


class Database:
    """Lightweight SQLite helper."""

    def __init__(self, path_to_db: str) -> None:
        self.path_to_db = path_to_db
        self._init_db()

    def _init_db(self):
        create_users = """
                       CREATE TABLE IF NOT EXISTS Users
                       (
                           is_allowed  INTEGER DEFAULT 0,
                           telegram_id INTEGER PRIMARY KEY,
                           full_name   TEXT
                       );
                       """
        create_chats = """
                        CREATE TABLE IF NOT EXISTS Chats
                        (
                            is_allowed INTEGER DEFAULT 0,
                            chat_id    INTEGER PRIMARY KEY,
                            title      TEXT
                        );
                        """
        create_requests = """
                          CREATE TABLE IF NOT EXISTS REQUESTS
                          (
                              id          INTEGER PRIMARY KEY AUTOINCREMENT,
                              req_time    TEXT,
                              req_text    TEXT,
                              req_user_id INTEGER,
                              req_resp    TEXT
                          );
                          """
        create_settings = """
                          CREATE TABLE IF NOT EXISTS UserSettings
                          (
                              telegram_id INTEGER PRIMARY KEY,
                              language    TEXT DEFAULT 'ru',
                              timezone    TEXT DEFAULT 'UTC',
                              color_q1    TEXT DEFAULT '#ff8c00',
                              color_q2    TEXT DEFAULT '#ff0000',
                              color_q3    TEXT DEFAULT '#00ff00',
                              color_q4    TEXT DEFAULT '#0000ff'
                          );
                          """

        with sqlite3.connect(self.path_to_db) as connection:
            cursor = connection.cursor()
            cursor.execute(create_users)
            cursor.execute(create_chats)
            cursor.execute(create_requests)
            cursor.execute(create_settings)
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

    def add_user(self, telegram_id: int, full_name: str, is_allowed: bool = False) -> None:
        if self.user_exists(telegram_id):
            logger.info("Пользователь %s уже существует", telegram_id)
            return
        sql = "INSERT INTO Users(telegram_id, full_name, is_allowed) VALUES(?, ?, ?);"
        self.execute(sql, (telegram_id, full_name, int(is_allowed)), commit=True)

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

    # Settings management

    def get_settings(self, telegram_id: int) -> dict | None:
        sql = (
            "SELECT language, timezone, color_q1, color_q2, color_q3, color_q4 "
            "FROM UserSettings WHERE telegram_id = ? LIMIT 1;"
        )
        row = self.execute(sql, (telegram_id,), fetchone=True)
        if row:
            return {
                "language": row[0],
                "timezone": row[1],
                "color_q1": row[2],
                "color_q2": row[3],
                "color_q3": row[4],
                "color_q4": row[5],
            }
        return None

    def set_settings(
        self,
        telegram_id: int,
        *,
        language: str | None = None,
        timezone: str | None = None,
        colors: tuple[str, str, str, str] | None = None,
    ) -> None:
        current = self.get_settings(telegram_id) or {}
        language = language or current.get("language", "ru")
        timezone = timezone or current.get("timezone", "UTC")
        c1, c2, c3, c4 = colors or (
            current.get("color_q1", "#ff8c00"),
            current.get("color_q2", "#ff0000"),
            current.get("color_q3", "#00ff00"),
            current.get("color_q4", "#0000ff"),
        )
        sql = (
            "INSERT OR REPLACE INTO UserSettings(telegram_id, language, timezone,"
            " color_q1, color_q2, color_q3, color_q4) VALUES(?, ?, ?, ?, ?, ?, ?);"
        )
        self.execute(
            sql,
            (telegram_id, language, timezone, c1, c2, c3, c4),
            commit=True,
        )

    # Chat management

    def add_chat(self, chat_id: int, title: str, is_allowed: bool = False) -> None:
        if self.chat_exists(chat_id):
            logger.info("Чат %s уже существует", chat_id)
            return
        sql = "INSERT INTO Chats(chat_id, title, is_allowed) VALUES(?, ?, ?);"
        self.execute(sql, (chat_id, title, int(is_allowed)), commit=True)

    def chat_exists(self, chat_id: int) -> bool:
        sql = "SELECT 1 FROM Chats WHERE chat_id = ? LIMIT 1;"
        return self.execute(sql, (chat_id,), fetchone=True) is not None

    def has_chat_access(self, chat_id: int) -> bool:
        sql = "SELECT is_allowed FROM Chats WHERE chat_id = ? LIMIT 1;"
        row = self.execute(sql, (chat_id,), fetchone=True)
        return bool(row and row[0])

    def set_chat_access(self, chat_id: int, allowed: bool) -> None:
        if self.chat_exists(chat_id):
            sql = "UPDATE Chats SET is_allowed = ? WHERE chat_id = ?;"
            self.execute(sql, (int(allowed), chat_id), commit=True)
        else:
            self.add_chat(chat_id, "", allowed)
