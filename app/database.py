import sqlite3
import os


class Database:
    def __init__(self, db_path: str, sql_file: str):
        """
        Ініціалізація класу Database.

        :param db_path: Шлях до файлу бази даних.
        :param sql_file: Шлях до SQL-файлу з інструкціями для створення.
        """
        self.db_path = db_path
        self.sql_file = sql_file
        self.connection = None

    def connect(self):
        """Підключення до бази даних."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            print(f"Підключено до бази даних: {self.db_path}")
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

    def get_table_columns(self, table_name):
        """Отримання списку стовпців таблиці table_name."""
        cursor = self.connection.execute(f'SELECT * FROM {table_name} WHERE 1=0')
        columns = [description[0] for description in cursor.description]
        return columns

    def add_record(self, table_name:str, columns, values):
        """Додавання нового запису в таблицю table_name."""
        query = f"""
        INSERT INTO {table_name} ({', '.join(columns)})
        VALUES ({', '.join(['?' for _ in values])})
        """
        try:
            with self.connection:
                self.connection.execute(query, values)
                # print(f"Новий запис для таблиці {table_name} успішно додано.")
        except sqlite3.Error as e:
            print(f"Помилка додавання запису: {e}")
            raise e

    def update_record(self, table_name:str, columns, values):
        """Оновлення існуючого запису в таблиці table_name."""
        query = f"""
        UPDATE {table_name} 
        SET {', '.join([f"{column} = ?" for column in columns])}
        WHERE id = ?
        """
        try:
            with self.connection:
                self.connection.execute(query, values)
                # print(f"Запис в таблиці {table_name} успішно оновлено.")
        except sqlite3.Error as e:
            print(f"Помилка оновлення запису: {e}")
            raise e

    def delete_record(self, table_name, record_id):
        """Видаляє запис з бази даних."""
        query = f"DELETE FROM {table_name} WHERE id = ?"
        try:
            with self.connection:
                self.connection.execute(query, (record_id,))
                # print("Запис видалено.")
        except sqlite3.Error as e:
            print(f"Помилка видалення: {e}")
            raise e
    
    def get_all_record(self, table_name):
        """Отримання списку всіх еементів з таблиці table_name."""
        query = f"SELECT * FROM {table_name}"
        try:
            with self.connection:
                cursor = self.connection.execute(query)
                return cursor.fetchall()
        except sqlite3.Error as e:
            raise e

    def add_user(self, values):
        column_name = self.get_table_columns("users")[1:]
        self.add_record("users", column_name, values)

    def update_user(self, record_id, values):
        column_name = self.get_table_columns("users")[1:]
        self.update_record("users", column_name, values + [record_id])

    def delete_user(self, record_id):
        self.delete_record("users", record_id)

    def get_users(self):
        return self.get_all_record("users")