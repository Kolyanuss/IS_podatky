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

    def execute_query(self, query: str, parameters: tuple = ()):
        """
        Виконання запиту до бази даних.

        :param query: SQL-запит.
        :param parameters: Параметри для запиту (якщо є).
        :return: Результати виконання запиту.
        """
        try:
            with self.connection:
                cursor = self.connection.execute(query, parameters)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Помилка виконання запиту: {e}")
            raise e

    def execute_non_query(self, query: str, parameters: tuple = ()):
        """
        Виконання запиту без повернення результату (INSERT, UPDATE, DELETE).

        :param query: SQL-запит.
        :param parameters: Параметри для запиту (якщо є).
        """
        try:
            with self.connection:
                self.connection.execute(query, parameters)
                print("Запит успішно виконано.")
        except sqlite3.Error as e:
            print(f"Помилка виконання запиту: {e}")
            raise e
