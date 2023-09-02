from tinydb import TinyDB

from app.AggroConfig import AggroConfig


class DatabaseManager:
    def __init__(self):
        self.db: TinyDB | None = None

    def setup(self, config: AggroConfig):
        self.db = TinyDB(config.db_path)


database_manager: DatabaseManager = DatabaseManager()
