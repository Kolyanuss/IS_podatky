from app.database import Database
from app.base_repository import BaseRepository

class UserRepository(BaseRepository):
    def __init__(self, database: Database):
        super().__init__(database)
        self.table_name = "users"
        self.columns = self.get_table_columns()
        
    def get_id_and_full_name(self):
        query = """
        SELECT
            users.id,
            users.last_name || ' ' || users.name || ' ' || users.middle_name AS fullname
        FROM users
        """
        return self.db.execute_query(query)
        