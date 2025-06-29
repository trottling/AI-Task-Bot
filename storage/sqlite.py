import logging
import sqlite3


logger = logging.getLogger(__name__)


class Database:
    """Lightweight SQLite helper."""

    def __init__(self, path_to_db: str) -> None:
        self.path_to_db = path_to_db

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

    def add_user(self, telegram_id: int, full_name: str) -> None:
        if self.user_exists(telegram_id):
            logger.info("User %s already exists", telegram_id)
            return
        sql = "INSERT INTO Users(telegram_id, full_name) VALUES(?, ?);"
        self.execute(sql, (telegram_id, full_name), commit=True)

    def user_exists(self, telegram_id: int) -> bool:
        sql = "SELECT 1 FROM Users WHERE telegram_id = ? LIMIT 1;"
        return self.execute(sql, (telegram_id,), fetchone=True) is not None

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM Users;", fetchone=True)

    def count_reqs(self):
        return self.execute("SELECT COUNT(*) FROM REQUESTS;", fetchone=True)
