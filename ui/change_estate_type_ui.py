from PyQt6.QtWidgets import (
    QPushButton, QLabel, QLineEdit, QVBoxLayout, QDialog, QMessageBox, QTableWidgetItem
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
from ui.styles import apply_style, get_button_style
from app.real_estate_type_repository import RealEstateTypeRepository
from app.database import Database


class EstateTypeDialog(QDialog):
    close_signal = pyqtSignal()
    def __init__(self, database:Database, year:int):
        super().__init__()
        self.estate_type_repo = RealEstateTypeRepository(database)
        self.year = year
        self.setWindowTitle("Типи нерухомості")
        self.setStyleSheet("background-color: #f0f4f8;")
        
        # self.load_data()


    def load_data(self):
        """Завантаження інформації з бази даних"""
        records = self.estate_type_repo.get_type_rates()
        print(records)
        
        self.table.setRowCount(len(records))
        for row_idx, row in enumerate(records):
            for col_idx, item in enumerate(row):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))
                
    def closeEvent(self, event):
        self.close_signal.emit()
        super().closeEvent(event)