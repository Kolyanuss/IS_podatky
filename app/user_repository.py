from app.database import Database
from app.base_repository import BaseRepository

class UserRepository(BaseRepository):
    def __init__(self, database: Database):
        super().__init__(database)
        self.table_name = "users"
        self.columns = self.get_table_columns()
        