from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QLineEdit, QPushButton, QWidget, QHBoxLayout, QMessageBox
)
from app.database import Database


class MainWindow(QMainWindow):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db

        self.setWindowTitle("Інформаційна система роботи з падатками")
        self.setGeometry(100, 100, 800, 600)

        # Основний віджет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Таблиця
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["id", "name", "last_name", "middle_name", "rnokpp", "address", "email", "phone"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Заборона прямого редагування
        self.table.cellClicked.connect(self.on_cell_click)

        # Поля вводу
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введіть name")

        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("Введіть last_name")

        self.middle_name_input = QLineEdit()
        self.middle_name_input.setPlaceholderText("Введіть middle_name")

        self.rnokpp_input = QLineEdit()
        self.rnokpp_input.setPlaceholderText("Введіть rnokpp")

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Введіть address")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Введіть email")

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Введіть phone")

        # Кнопки
        self.add_button = QPushButton("Додати")
        self.add_button.clicked.connect(self.add_record)

        self.update_button = QPushButton("Оновити")
        self.update_button.clicked.connect(self.load_data)

        self.delete_button = QPushButton("Видалити")
        self.delete_button.clicked.connect(self.delete_record)

        self.inputs = [
            self.name_input, self.last_name_input, self.middle_name_input, self.rnokpp_input, self.address_input, self.email_input, self.phone_input
        ]

        # Розташування
        form_layout = QHBoxLayout()
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.last_name_input)
        form_layout.addWidget(self.middle_name_input)
        form_layout.addWidget(self.rnokpp_input)
        form_layout.addWidget(self.address_input)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.phone_input)
        
        form_layout.addWidget(self.add_button)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)

        self.central_widget.setLayout(layout)

        # Завантаження даних
        self.load_data()

    def load_data(self):
        """Завантаження даних у таблицю."""
        records = self.db.execute_query("SELECT * FROM users")
        self.table.setRowCount(len(records))
        for row_idx, row_data in enumerate(records):
            for col_idx, col_data in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

    def add_record(self):
        """Додавання запису в базу даних."""
        data = [item.text() for item in self.inputs]
                
        if all(data):
            self.db.execute_non_query(
                "INSERT INTO users (name, last_name, middle_name, rnokpp, address, email, phone) VALUES (?, ?, ?, ?, ?, ?, ?)", (*data,)
            )
            for item in self.inputs:
                item.clear()
            self.load_data()
        else:
            QMessageBox.warning(self, "Помилка", "Заповніть усі поля!")

    def delete_record(self):
        """Видалення вибраного запису."""
        selected_row = self.table.currentRow()
        if selected_row != -1:
            record_id = self.table.item(selected_row, 0).text()
            self.db.execute_non_query("DELETE FROM users WHERE id = ?", (record_id,))
            self.load_data()
        else:
            QMessageBox.warning(self, "Помилка", "Виберіть запис для видалення!")

    def on_cell_click(self, row, column):
        """Обробка кліку на клітинку (якщо потрібно)."""
        print(f"Вибраний рядок: {row}, колонка: {column}")
