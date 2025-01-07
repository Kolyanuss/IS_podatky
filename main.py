import sys, shutil, os
from pathlib import Path
from datetime import datetime
from app.database import Database
from ui.main_window_ui import MainWindow
from PyQt6.QtWidgets import QApplication


def backup_database():
    """Функція резервного копіювання бази даних."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    timestamp = datetime.now().strftime("%Y-%m-%d__%H-%M")
    backup_name = f"db_backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    try:
        shutil.copy(DB_PATH, backup_path)
        print(f"Резервна копія створена: {backup_path}")
    except Exception as e:
        print(f"Помилка під час копіювання: {e}")

if __name__ == "__main__":
    sql_file = "db/db.sql"
    data_folder_name = ".IS_podatky_data"
    app_data_path = os.path.join(Path.home(), data_folder_name)
    if not os.path.exists(app_data_path):
        os.makedirs(app_data_path)

    DB_PATH = os.path.join(app_data_path, "db.db")
    BACKUP_DIR = os.path.join(app_data_path, "backup")

    app = QApplication(sys.argv)
    app.aboutToQuit.connect(backup_database)

    db = Database(DB_PATH, sql_file)
    db.initialize_database()
    
    window = MainWindow(db)
    window.show()

    sys.exit(app.exec())
