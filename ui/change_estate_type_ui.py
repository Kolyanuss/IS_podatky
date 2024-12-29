from PyQt6.QtWidgets import (
    QPushButton, QLabel, QLineEdit, QVBoxLayout, QDialog, QMessageBox, QTableWidgetItem
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
from ui.styles import apply_styles, get_button_style
from ui.utils import create_table_widget
from app.real_estate_type_repository import RealEstateTypeRepository
from app.database import Database


class EstateTypeDialog(QDialog):
    close_signal = pyqtSignal()
    def __init__(self, database:Database, year:int):
        super().__init__()
        self.estate_type_repo = RealEstateTypeRepository(database)
        self.year = year
        self.input_fields = {}
        
        self.init_ui()
        # self.load_data()

    def init_ui(self):
        """Ініціалізація основного інтерфейсу"""
        self.setWindowTitle("Типи нерухомості")
        self.setStyleSheet("background-color: #f0f4f8;")
        self.setGeometry(100, 100, 1200, 700)
        
        apply_styles(self, ["base", "input_field", "label"])
        
        self.table = create_table_widget(8, ["Id"]+[item[1] for item in self.fields_config], self.on_cell_click)
        
        input_container = self.create_input_container()
        
        button_layout = self.create_buttons()
        
        # Компонування основного лейауту
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.table)
        main_layout.addWidget(input_container)
        main_layout.addLayout(button_layout)
        

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