import sqlite3
import os, shutil
from datetime import datetime

class UniqueFieldException(Exception):
    pass


class Database:
    def __init__(self, app_data_path: str, sql_file: str):
        """
        Ініціалізація класу Database.

        :param db_path: Шлях до файлу бази даних.
        :param sql_file: Шлях до SQL-файлу з інструкціями для створення.
        """
        self.db_path = os.path.join(app_data_path, "db.db")
        self.backup_dir = os.path.join(app_data_path, "backup")
        self.sql_file = sql_file
        self.connection = None
        
        self.initialize_database()

    def connect(self):
        """Підключення до бази даних."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            print(f"Підключено до бази даних: {self.db_path}")
            self.connection.execute("PRAGMA foreign_keys = ON;")
        except sqlite3.Error as e:
            print(f"Помилка підключення до бази даних: {e}")
            raise e

    def close(self):
        """Закриття з'єднання з базою даних."""
        if self.connection:
            self.connection.close()
            print("З'єднання з базою даних закрито.")

    def initialize_database(self):
        """
        Ініціалізація бази даних із SQL-скрипту.
        Якщо база даних не існує, створюється нова структура.
        """
        if not os.path.exists(self.db_path):
            print("База даних не знайдена. Ініціалізація...")
            try:
                # Створення підключення для виконання SQL-скрипту
                self.connection = sqlite3.connect(self.db_path)
                with open(self.sql_file, 'r') as file:
                    sql_script = file.read()

                with self.connection:
                    self.connection.executescript(sql_script)
                print("База даних успішно створена.")
            except (sqlite3.Error, FileNotFoundError) as e:
                print(f"Помилка ініціалізації бази даних: {e}")
                raise e
        else:
            print("База даних вже існує. Пропускаю ініціалізацію.")
            # Підключення до існуючої бази
            self.connect()

    def execute_query(self, query: str, params: tuple = None):
        try:
            with self.connection:
                cursor = self.connection.execute(query, params or ())
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Помилка запиту отримання даних: {e}")
            raise e
    
    def execute_non_query(self, query: str, params: tuple = None):
        '''Повертає ID елемента'''
        try:
            with self.connection:
                cursor = self.connection.execute(query, params or ())
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Помилка запиту зміни даних: {e}")
            if "UNIQUE" in str(e):
                raise UniqueFieldException()
            raise e

    def save_DB_backup(self):
        """Функція резервного копіювання бази даних."""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        timestamp = datetime.now().strftime("%Y-%m-%d__%H-%M")
        backup_name = f"db_backup_{timestamp}.db"
        backup_path = os.path.join(self.backup_dir, backup_name)
        try:
            self.close()
            shutil.copy(self.db_path, backup_path)
            print(f"Резервна копія створена: {backup_path}")
            self.connect()
        except Exception as e:
            print(f"Помилка під час копіювання: {e}")
            
    def load_DB_backup(self, file_path):
        """Функція відновлення бази даних із резервної копії."""
        if not os.path.exists(file_path):
            print(f"Файл резервної копії не знайдено: {file_path}")
            return False
        
        # Перевіряємо чи файл є SQLite базою даних
        try:
            with open(file_path, 'rb') as file:
                header = file.read(16)
                if header[:16] != b'SQLite format 3\x00':  # Перевірка магічного числа SQLite
                    print("Файл не є валідною базою даних SQLite")
                    return False
            
            # Додаткова перевірка через підключення
            test_connection = sqlite3.connect(file_path)
            test_connection.close()
            
        except (sqlite3.Error, IOError) as e:
            print(f"Помилка перевірки файлу бази даних: {e}")
            return False
        
        # відновлення
        try:
            self.close()
            shutil.copy(file_path, self.db_path)
            self.connect()
            return True
        except Exception as e:
            print(f"Помилка при відновленні бази: {e}")
            return False