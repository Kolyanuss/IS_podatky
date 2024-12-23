from app.database import Database
from ui.ui import MainWindow
import sys
from PyQt5.QtWidgets import QApplication

# Приклад використання
if __name__ == "__main__":
    db_path = "db/db.db"
    sql_file = "db/db.sql"

    app = QApplication(sys.argv)

    db = Database(db_path, sql_file)
    db.initialize_database()


    window = MainWindow(db)
    window.show()

    sys.exit(app.exec_())
