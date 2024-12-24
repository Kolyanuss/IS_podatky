from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QFrame, 
    QTableWidget, QTableWidgetItem, QHBoxLayout, QLabel, QHeaderView
)

class AddPersonDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.input_fields = {}
        self.fields_config = [
            ("name", "Ім'я*", "Введіть ім'я"),
            ("last_name", "Прізвище*", "Введіть прізвище"),
            ("middle_name", "По батькові*", "Введіть по батькові"),
            ("rnokpp", "РНОКПП*", "Введіть РНОКПП"),
            ("address", "Адреса*", "Введіть адресу"),
            ("email", "Email", "Введіть email"),
            ("phone", "Телефон", "Введіть телефон")
        ]
        
        self.init_ui()
        self.load_users()

    def init_ui(self):
        """Ініціалізація основного інтерфейсу"""
        self.setWindowTitle("Керування користувачами")
        self.resize(1200, 700)
        # self.apply_global_styles()
        
        # Створення основних компонентів
        self.create_table()
        input_container = self.create_input_container()
        button_layout = self.create_buttons()
        
        # Компонування основного лейауту
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.table)
        main_layout.addWidget(input_container)
        main_layout.addLayout(button_layout)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        self.setLayout(main_layout)

    def apply_global_styles(self):
        """Застосування глобальних стилів"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f6fa;
                font-family: 'Segoe UI', sans-serif;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #dcdde1;
                border-radius: 5px;
                gridline-color: #636e72;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #dcdde1;
                border-right: 1px solid #dcdde1;
            }
            QHeaderView::section {
                background-color: #f5f6fa;
                padding: 5px;
                border: none;
                font-weight: bold;
                border-bottom: 2px solid #2d3436;
                border-right: 1px solid #dcdde1;
            }
            QHeaderView::section:last {
                border-right: none;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #dcdde1;
                border-radius: 5px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QPushButton:hover {
                opacity: 0.8;
                margin: 0px;
                border: 1px solid #636e72;
            }
            QPushButton:pressed {
                margin: 2px 0px 0px 2px;
            }
            QLabel {
                color: #2f3640;
                font-weight: bold;
            }
        """)

    def create_table(self):
        """Створення та налаштування таблиці"""
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Ім'я", "Прізвище", "По батькові", 
            "РНОКПП", "Адреса", "Email", "Телефон"
        ])
        self.table.setColumnHidden(0, True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.cellClicked.connect(self.on_cell_click)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #dcdde1;
                background-color: white;
                border: 1px solid #dcdde1;
            }
            QTableWidget::item:selected {
                background-color: #74b9ff;
                color: black;
            }
            QTableWidget::item:alternate {
                background-color: #f5f6fa;
            }
        """)

    def create_input_field(self, label_text, placeholder):
        """Створення окремого поля вводу з міткою"""
        field_layout = QVBoxLayout()
        
        label = QLabel(label_text)
        
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        
        field_layout.addWidget(label)
        field_layout.addWidget(input_field)
        
        return field_layout, input_field

    def create_input_container(self):
        """Створення контейнера з полями вводу"""
        input_container = QFrame()
        input_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 5px;
                border: 1px solid #dcdde1;
            }
        """)
        
        input_grid = QHBoxLayout(input_container)
        input_grid.setSpacing(10)

        # Конфігурація полів вводу
        for field_name, label_text, placeholder in self.fields_config:
            field_layout, input_field = self.create_input_field(label_text, placeholder)
            self.input_fields[field_name] = input_field
            input_grid.addLayout(field_layout)

        return input_container

    def create_button(self, text, color, hover_color, callback):
        """Створення кнопки з заданими параметрами"""
        button = QPushButton(text)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                padding: 5px 10px;
                border-radius: 5px;
                border: none;
                color: white;
                font-weight: bold;
                font-size: 20px;
                margin: 1px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                margin: 0px;
                border: 1px solid #636e72;
            }}
            QPushButton:pressed {{
                margin: 2px 0px 0px 2px;
                background-color: {color};
            }}
            """)
        button.clicked.connect(callback)
        return button

    def create_buttons(self):
        """Створення панелі з кнопками"""
        button_layout = QHBoxLayout()
        
        self.add_button = self.create_button("Додати", "#2ecc71", "#27ae60", self.add_person)
        self.update_button = self.create_button("Оновити", "#3498db", "#2980b9", self.update_person)
        self.delete_button = self.create_button("Видалити", "#e74c3c", "#c0392b", self.delete_record)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.setSpacing(15)
        
        return button_layout

    def load_users(self):
        """Завантаження користувачів у таблицю."""
        users = self.db.get_users()
        self.table.setRowCount(len(users))
        for row_idx, user in enumerate(users):
            for col_idx, data in enumerate(user):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))

    def add_person(self):
        """Додавання нового користувача в базу даних."""
        data = [field.text() for field in self.input_fields.values()]

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
            data = [field.text() for field in self.input_fields.values()]

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
        i = 1
        for field in self.input_fields.values():
            field.setText(self.table.item(row, i).text())
            i += 1

    def clear_inputs(self):
        """Очищення всіх полів введення."""
        for field in self.input_fields.values():
            field.clear()
