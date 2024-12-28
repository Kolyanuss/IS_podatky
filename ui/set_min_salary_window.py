import time
from PyQt6.QtWidgets import (
    QPushButton, QLabel, QLineEdit, QVBoxLayout, QDialog, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
from ui.styles import apply_style, get_button_style
from app.salary_repository import SalaryRepository
from app.database import Database


class MinSalaryWindow(QDialog):
    close_signal = pyqtSignal()
    def __init__(self, database:Database, year:int):
        super().__init__()
        self.salary_repository = SalaryRepository(database)
        self.year = year
        self.setWindowTitle("Мінімальна зарплата")
        self.setStyleSheet("background-color: #f0f4f8;")
        self.setFixedSize(560,150)
        
        # Заголовок
        label = QLabel("Введіть мінімальну зарплату за попередній рік:")
        label.setFont(QFont("Arial", 18))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: #333; margin-bottom: 10px;")

        # Поле вводу
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Мінімальна зарплата")
        self.input_field.setStyleSheet("""
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 5px;
            font-size: 18px;
        """)
        if record := self.salary_repository.get_record_by_id(self.year):
            self.input_field.setText(f"{record[1]}")
        
        # Кнопка "Підтвердити"
        self.confirm_button = QPushButton("Підтвердити")
        self.confirm_button.setStyleSheet(get_button_style("success"))
        self.confirm_button.clicked.connect(self.confirm_action)

        # Вертикальний макет
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.input_field)
        layout.addWidget(self.confirm_button)
        self.setLayout(layout)

    def confirm_action(self):
        value = self.input_field.text()
        if not value.isdigit():
            self.confirm_button.setStyleSheet(get_button_style("warning"))
            QMessageBox().critical(self, "Помилка", "Введене значення не є числом! Спробуйте ще раз.")
            return
        
        self.salary_repository.add_update_record(self.year, value)
        self.close()

    def closeEvent(self, event):
        self.close_signal.emit()
        super().closeEvent(event)