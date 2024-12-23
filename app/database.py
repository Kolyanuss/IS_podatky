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

    def add_user(self, name, last_name, middle_name, rnokpp, address, email, phone):
        """Додавання нового користувача."""
        query = """
        INSERT INTO users (name, last_name, middle_name, rnokpp, address, email, phone)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        try:
            with self.connection:
                self.connection.execute(query, (name, last_name, middle_name, rnokpp, address, email, phone))
                print("Користувача успішно додано.")
        except sqlite3.Error as e:
            print(f"Помилка додавання користувача: {e}")
            raise e

    def update_user(self, record_id, name, last_name, middle_name, rnokpp, address, email, phone):
        """Оновлює інформацію про користувача в базі даних."""
        query = """
        UPDATE users
        SET name = ?, last_name = ?, middle_name = ?, rnokpp = ?, address = ?, email = ?, phone = ?
        WHERE id = ?
        """
        try:
            with self.connection:
                self.connection.execute(query, (name, last_name, middle_name, rnokpp, address, email, phone, record_id))
                print("Дані користувача оновлено.")
        except sqlite3.Error as e:
            print(f"Помилка оновлення користувача: {e}")
            raise e

    def delete_user(self, record_id):
        """Видаляє запис користувача з бази даних."""
        query = "DELETE FROM users WHERE id = ?"
        try:
            with self.connection:
                self.connection.execute(query, (record_id,))
                print("Користувача видалено.")
        except sqlite3.Error as e:
            print(f"Помилка видалення користувача: {e}")
            raise e

    def get_users(self):
        """Отримання списку користувачів."""
        query = "SELECT * FROM users"
        try:
            with self.connection:
                cursor = self.connection.execute(query)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Помилка отримання користувачів: {e}")
            raise e