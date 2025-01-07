from PyQt6.QtWidgets import (QDialog, QVBoxLayout, 
    QLineEdit, QPushButton, QLabel, QMessageBox)
from ui.styles import apply_styles, get_button_style

class InputNMVDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Зміна значеня нормативно грошової оцінки")
        self.setFixedSize(300, 200)

        self.main_layout = QVBoxLayout()
        
        self.label1 = QLabel("Змінити старе значення:")
        self.input1 = QLineEdit()
        self.main_layout.addWidget(self.label1)
        self.main_layout.addWidget(self.input1)

        self.label2 = QLabel("На нове значення:")
        self.input2 = QLineEdit()
        self.input2.setStyleSheet("margin-bottom: 5px;")
        self.main_layout.addWidget(self.label2)
        self.main_layout.addWidget(self.input2)

        self.submit_button = QPushButton("Підтвердити")
        self.submit_button.clicked.connect(self.submit_values)
        self.submit_button.setStyleSheet(get_button_style("success"))
        self.main_layout.addWidget(self.submit_button)

        apply_styles(self, ["input_field", "label"])
        
        self.setLayout(self.main_layout)

    def submit_values(self):
        value1 = self.input1.text()
        value2 = self.input2.text()

        if not value1 or not value2:
            self.submit_button.setStyleSheet(get_button_style("warning"))
            QMessageBox.warning(self, "Помилка", "Будь ласка, заповніть обидва поля.")
            return

        try:
            float(value1),float(value2)
        except Exception as e:
            self.submit_button.setStyleSheet(get_button_style("warning"))
            QMessageBox.warning(self, "Помилка", "Значення повинні бути числовими")
            return

        self.value1 = value1
        self.value2 = value2

        self.accept()