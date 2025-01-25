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
            users.last_name || ' ' || users.name || ' ' || users.middle_name || ' ' || users.rnokpp AS fullname
        FROM users
        """
        return self.db.execute_query(query)
    
    def get_record_by_code(self, code):
        query = f"""
        SELECT * FROM {self.table_name}
        WHERE rnokpp = ?
        """
        result = self.db.execute_query(query, (code,))
        return result[0] if result else None
        