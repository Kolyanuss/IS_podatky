from PyQt6.QtWidgets import (
    QPushButton, QLabel, QLineEdit, QVBoxLayout, QDialog,
    QMessageBox, QTableWidgetItem, QFrame, QHBoxLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
from ui.styles import apply_style, apply_styles, get_button_style
from ui.utils import create_table_widget, create_CUD_buttons, create_Vbox
from app.real_estate_type_repository import RealEstateTypeRepository
from app.database import Database


class EstateTypeDialog(QDialog):
    close_signal = pyqtSignal()
    def __init__(self, database:Database, year:int):
        super().__init__()
        self.estate_type_repo = RealEstateTypeRepository(database)
        self.year = year
        self.input_fields = {}
        self.fields_config = [
            ("type", "Тип", "Введіть назву типу*"),
            ("rate", "Ставка %", "Введіть ставку*"),
            ("limit", "Ліміт площі", "Введіть ліміт площі*"),
        ]
        
        self.init_ui()
        # self.load_data()

    def init_ui(self):
        """Ініціалізація основного інтерфейсу"""
        self.setWindowTitle("Типи нерухомості")
        self.setStyleSheet("background-color: #f0f4f8;")
        self.setGeometry(100, 100, 1200, 700)
        
        apply_styles(self, ["base", "input_field", "label"])
        
        columns = self.estate_type_repo.columns
        self.table = create_table_widget(len(self.fields_config)+1, ["id"]+[item[1] for item in self.fields_config], self.on_cell_click)
        
        input_container = self.create_input_container()
        
        button_layout = create_CUD_buttons(self.add_record, self.update_record, self.delete_record)
        
        # Компонування основного лейауту
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.table)
        main_layout.addWidget(input_container)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
    def create_input_container(self):
        """Створення контейнера з полями вводу"""
        input_container = QFrame()
        input_container.setObjectName("inputContainer")
        apply_style(input_container, "input_container")
        
        input_grid = QHBoxLayout(input_container)
        input_grid.setSpacing(10)

        # Конфігурація полів вводу
        for field_name, label_text, placeholder in self.fields_config:
            line = QLineEdit()
            line.setPlaceholderText(placeholder)
            field_layout, input_field = create_Vbox(label_text, line)
            self.input_fields[field_name] = input_field
            input_grid.addLayout(field_layout)

        return input_container

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
        
    def on_cell_click(self, row, column):
        """Заповнення полів введення даними вибраного рядка."""        
        i = 1
        for field in self.input_fields.values():
            field.setText(self.table.item(row, i).text())
            i += 1
    
    def add_record(self):
        """Додавання запису"""
        pass        

    def update_record(self):
        """Оновлення запису"""
        pass

    def delete_record(self):
        """Видалення запису"""
        pass      