import sqlite3
from pathlib import Path


class Database:

    def __init__(self, database_path):

        self.database_path = Path(database_path)

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    def connect(self):

        return sqlite3.connect(
            self.database_path
        )

    def execute(
        self,
        query,
        parameters=()
    ):

        with self.connect() as connection:

            cursor = connection.cursor()

            cursor.execute(
                query,
                parameters
            )

            connection.commit()

            return cursor

    def fetch_one(
        self,
        query,
        parameters=()
    ):

        with self.connect() as connection:

            cursor = connection.cursor()

            cursor.execute(
                query,
                parameters
            )

            return cursor.fetchone()

    def fetch_all(
        self,
        query,
        parameters=()
    ):

        with self.connect() as connection:

            cursor = connection.cursor()

            cursor.execute(
                query,
                parameters
            )

            return cursor.fetchall()