from tinydb import TinyDB

from app.AggroConfig import AggroConfig


class DatabaseManager:
    def __init__(self):
        self.db: TinyDB | None = None

    def setup(self, config: AggroConfig):
        self.db = TinyDB(config.db_path)
        self.plugin_states = self.db.table("plugin_states")  # type: ignore
        self.feeds = self.db.table("feeds")  # type: ignore
        self.meta_info = self.db.table("meta_info")  # type: ignore


database_manager: DatabaseManager = DatabaseManager()
