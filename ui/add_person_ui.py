from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QFormLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QLabel, QHeaderView
)

class AddPersonDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Керування користувачами")
        self.resize(1000, 600)

        # Таблиця для перегляду користувачів
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Ім'я", "Прізвище", "По батькові", "РНОКПП", "Адреса", "Email", "Телефон"])
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.cellClicked.connect(self.on_cell_click)

        # Поля для введення даних
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("ім'я")

        self.last_name_input = QLineEdit()
        self.last_name_input.setPlaceholderText("прізвище")

        self.middle_name_input = QLineEdit()
        self.middle_name_input.setPlaceholderText("по батькові")

        self.rnokpp_input = QLineEdit()
        self.rnokpp_input.setPlaceholderText("РНОКПП")

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("адреса")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("email")

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("телефон")

        # Розташування елементів
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Ім'я*:"))
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(QLabel("Прізвище*:"))
        input_layout.addWidget(self.last_name_input)
        input_layout.addWidget(QLabel("По батькові*:"))
        input_layout.addWidget(self.middle_name_input)
        input_layout.addWidget(QLabel("РНОКПП*:"))
        input_layout.addWidget(self.rnokpp_input)
        input_layout.addWidget(QLabel("Адреса*:"))
        input_layout.addWidget(self.address_input)
        input_layout.addWidget(QLabel("Email:"))
        input_layout.addWidget(self.email_input)
        input_layout.addWidget(QLabel("Телефон:"))
        input_layout.addWidget(self.phone_input)

        # Кнопки
        self.add_button = QPushButton("Додати")
        self.add_button.clicked.connect(self.add_person)

        self.update_button = QPushButton("Оновити")
        self.update_button.clicked.connect(self.update_person)

        self.delete_button = QPushButton("Видалити")
        self.delete_button.clicked.connect(self.delete_record)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)

        # Основне розташування
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(input_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Завантаження даних у таблицю
        self.load_users()

    def load_users(self):
        """Завантаження користувачів у таблицю."""
        users = self.db.get_users()
        self.table.setRowCount(len(users))
        for row_idx, user in enumerate(users):
            for col_idx, data in enumerate(user):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))

    def add_person(self):
        """Додавання нового користувача в базу даних."""
        data = [
            self.name_input.text(),
            self.last_name_input.text(),
            self.middle_name_input.text(),
            self.rnokpp_input.text(),
            self.address_input.text(),
            self.email_input.text(),
            self.phone_input.text(),
        ]

        if all(data[:-2]):
            try:
                self.db.add_user(*data)
                QMessageBox.information(self, "Успіх", "Користувача успішно додано!")
                self.clear_inputs()
                self.load_users()
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося додати користувача: {e}")
        else:
            QMessageBox.warning(self, "Помилка", "Заповніть усі поля!")

    def update_person(self):
        """Оновлення вибраного користувача."""
        selected_row = self.table.currentRow()
        if selected_row != -1:
            record_id = self.table.item(selected_row, 0).text()
            data = [
                self.name_input.text(),
                self.last_name_input.text(),
                self.middle_name_input.text(),
                self.rnokpp_input.text(),
                self.address_input.text(),
                self.email_input.text(),
                self.phone_input.text(),
            ]

            if all(data[:-2]):
                try:
                    self.db.update_user(record_id, *data)
                    QMessageBox.information(self, "Успіх", "Дані користувача оновлено!")
                    self.clear_inputs()
                    self.load_users()
                except Exception as e:
                    QMessageBox.critical(self, "Помилка", f"Не вдалося оновити користувача: {e}")
            else:
                QMessageBox.warning(self, "Помилка", "Заповніть усі поля!")
        else:
            QMessageBox.warning(self, "Помилка", "Виберіть запис для оновлення!")

    def delete_record(self):
        """Видалення вибраного запису."""
        selected_row = self.table.currentRow()
        if selected_row != -1:
            record_id = self.table.item(selected_row, 0).text()
            try:
                self.db.delete_user(record_id)
                QMessageBox.information(self, "Успіх", "Користувача видалено!")
                self.load_users()
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося видалити користувача: {e}")
        else:
            QMessageBox.warning(self, "Помилка", "Виберіть запис для видалення!")

    def on_cell_click(self, row, column):
        """Заповнення полів введення даними вибраного рядка."""
        self.name_input.setText(self.table.item(row, 1).text())
        self.last_name_input.setText(self.table.item(row, 2).text())
        self.middle_name_input.setText(self.table.item(row, 3).text())
        self.rnokpp_input.setText(self.table.item(row, 4).text())
        self.address_input.setText(self.table.item(row, 5).text())
        self.email_input.setText(self.table.item(row, 6).text())
        self.phone_input.setText(self.table.item(row, 7).text())

    def clear_inputs(self):
        """Очищення всіх полів введення."""
        self.name_input.clear()
        self.last_name_input.clear()
        self.middle_name_input.clear()
        self.rnokpp_input.clear()
        self.address_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
