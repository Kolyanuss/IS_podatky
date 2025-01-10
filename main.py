import sys, os
from pathlib import Path
from app.database import Database
from ui.main_window_ui import MainWindow
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    sql_file = resource_path("db/db.sql")
    data_folder_name = ".IS_podatky_data"
    app_data_path = os.path.join(Path.home(), data_folder_name)
    if not os.path.exists(app_data_path):
        os.makedirs(app_data_path)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('Icon.ico'))
    
    db = Database(app_data_path, sql_file)
    
    window = MainWindow(db)
    window.show()

    sys.exit(app.exec())
