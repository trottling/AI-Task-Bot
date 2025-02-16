import sqlite3


class Database:
    def __init__(self, path_to_db):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone = False, fetchall = False, commit = False):
        if not parameters:
            parameters = ()
        connection = self.connection
        connection.set_trace_callback(logger)
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        connection.close()
        return data

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
            ])
        return sql, tuple(parameters.values())

    def add_user(self, telegram_id: int, full_name: str):
        sql = """INSERT INTO Users(telegram_id, full_name) VALUES(?, ?);"""
        self.execute(sql, parameters=(telegram_id, full_name), commit=True)

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM Users;", fetchone=True)

    def add_req(self, telegram_id: int, full_name: str):
        sql = """INSERT INTO Users(telegram_id, full_name) VALUES(?, ?);"""
        self.execute(sql, parameters=(telegram_id, full_name), commit=True)

    def count_reqs(self):
        return self.execute("SELECT COUNT(*) FROM REQUESTS;", fetchone=True)



def logger(statement):
    print(f"""
_____________________________________________________        
Executing: 
{statement}
_____________________________________________________
""")
