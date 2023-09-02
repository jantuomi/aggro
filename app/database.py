from tinydb import TinyDB

from app.AggroConfig import AggroConfig


def setup_db(config: AggroConfig):
    global database_manager
    database_manager = DatabaseManager(config)


class DatabaseManager:
    def __init__(self, config: AggroConfig):
        self.db = TinyDB(config.db_path)


database_manager: DatabaseManager
