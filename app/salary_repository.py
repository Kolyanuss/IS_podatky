from app.database import Database
from app.base_repository import BaseRepository

class SalaryRepository(BaseRepository):
    def __init__(self, database:Database):
        super().__init__(database)
        self.table_name = "general_info"
        self.columns = self.get_table_columns()
    
    def add_record(self, values):
        """Додавання нового запису в таблицю."""
        query = f"""
        INSERT INTO {self.table_name} ({', '.join(self.columns)})
        VALUES (?, ?)
        """
        self.db.execute_non_query(query, values)
    
    def add_update_record(self, record_id, value):
        """Додавання або оновлення існуючого запису в таблиці."""
        if self.get_record_by_id(record_id):
            self.update_record(record_id, (value,))
        else:
            self.add_record((record_id, value))