from app.database import Database

# Приклад використання
if __name__ == "__main__":
    db_path = "db/db.db"
    sql_file = "db/db.sql"

    db = Database(db_path, sql_file)
    db.initialize_database()

    # Приклади запитів
    try:
        # Додавання даних
        db.execute_non_query(
            "INSERT INTO general_info (year,min_salary,tax_rate,normative_monetary_value) VALUES (?, ?, ?, ?)",
            (2024, 8000, 1.05, 1.1)
        )

        # Читання даних
        items = db.execute_query("SELECT * FROM general_info")
        for item in items:
            print(item)

        # Оновлення даних
        db.execute_non_query(
            "UPDATE general_info SET min_salary = ? WHERE year = ?",
            (8500, 2024)
        )
        
        # Читання даних
        items = db.execute_query("SELECT * FROM general_info")
        for item in items:
            print(item)

        # Видалення даних
        db.execute_non_query(
            "DELETE FROM general_info WHERE year = ?",
            (2024,)
        )
    finally:
        # Закриття з'єднання
        db.close()
