import sys
from app.database import Database
from ui.main_window_ui import MainWindow
from PyQt6.QtWidgets import QApplication

# Приклад використання
if __name__ == "__main__":
    db_path = "db/db.db"
    sql_file = "db/db.sql"

    app = QApplication(sys.argv)

    db = Database(db_path, sql_file)
    db.initialize_database()

    window = MainWindow(db)
    window.show()

    sys.exit(app.exec())
