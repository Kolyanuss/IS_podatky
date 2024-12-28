from app.database import Database
import sqlite3

class BaseRepository:
    def __init__(self, database: Database):
        self.db = database
        self.table_name = ""
        self.columns = []
    
    def get_table_columns(self):
        """Отримання списку стовпців таблиці."""
        cursor = self.db.connection.execute(f'SELECT * FROM {self.table_name} WHERE 1=0')
        columns = [description[0] for description in cursor.description]
        return columns

    def get_all_record(self):
        """Отримання списку всіх елементів з таблиці."""
        query = f"SELECT * FROM {self.table_name}"
        return self.db.execute_query(query)
    
    def get_record_by_id(self, record_id):
        query = f"SELECT * FROM {self.table_name} WHERE {self.columns[0]} = ?"
        results = self.db.execute_query(query, (record_id,))
        return results[0] if results else None
    
    def add_record(self, values):
        """Додавання нового запису в таблицю."""
        query = f"""
        INSERT INTO {self.table_name} ({', '.join(self.columns[1:])})
        VALUES ({', '.join(['?' for _ in values])})
        """
        self.db.execute_non_query(query, values)

    def update_record(self, record_id, values):
        """Оновлення існуючого запису в таблиці."""
        query = f"""
        UPDATE {self.table_name} 
        SET {', '.join([f"{column} = ?" for column in self.columns[1:]])}
        WHERE {self.columns[0]} = ?
        """
        self.db.execute_non_query(query, tuple(values) + (record_id,))

    def delete_record(self, record_id):
        """Видаляє запис з таблиці."""
        query = f"DELETE FROM {self.table_name} WHERE {self.columns[0]} = ?"
        self.db.execute_non_query(query, (record_id,))
    